import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db.models import transaction
class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Mutations
class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType) 
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(lambda: CreateCustomer.Arguments)
    @classmethod
    @transaction.atomic
    def mutate(cls, root,info, input):
        created = []
        errors = []
        for item in input:
            try:
                customer = Customer.objects.create(name=item.name, email=item.email, phone=getattr(item, 'phone', None));
                customer.full_clean()
                customer.save()
                created.append(customer)
            except Exception as e:
                errors.append(f'{item.name}: {str(e)}')
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProduct(graphene.Mutation):
    Product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Int(required=True)
        stock = graphene.Int()

    def mutate(self, info, name, price, stock=0):
        if price < 0:
            raise ValidationError("Price must be non-negative.")
        if stock < 0:
            raise ValidationError("Stock must be non-negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Invalid customer ID")
        except Exception as e:
            raise ValidationError(f"Error creating order: {str(e)}")

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            raise ValidationError("Invalid product IDs")

        order = Order(customer=customer)
        order.save()
        order.products.set(products)
        order.total_amount = sum(p.price for p in products)
        order.save()
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class CRMQuery(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")