from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.text import slugify

# RF01 - Proveedores
# En models.py, modifica el modelo Proveedor:
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.CharField(max_length=150)
    
    # NUEVOS CAMPOS PARA VISTA PÚBLICA
    logo = models.ImageField(upload_to='proveedores/logos/', null=True, blank=True)
    descripcion = models.TextField(blank=True, help_text="Descripción pública del proveedor")
    sitio_web = models.URLField(blank=True)
    activo = models.BooleanField(default=True, help_text="Mostrar en página pública")
    
    def __str__(self):
        return self.nombre
    
    @property
    def logo_url(self):
        if self.logo:
            return self.logo.url
        return '/static/tienda/images/default-provider.png'


# RF02 - Categorías
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# RF04 - Tallas
class Talla(models.Model):
    nombre = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre

# RF05 - Colores
class Color(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(unique=False, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='productos'
    )

    imagen = models.ImageField(
        upload_to='productos/',
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True)
    es_destacado = models.BooleanField(default=False)
    
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    @property
    def precio_final(self):
        return self.precio_oferta if self.precio_oferta else self.precio

    @property
    def en_oferta(self):
        return self.precio_oferta is not None and self.precio_oferta < self.precio

    @property
    def estado_stock(self):
        total = self.stock
        if total == 0:
            return "out"
        elif total <= 5:
            return "last"
        return "in"

    @property
    def imagen_url(self):
        if self.imagen:
            return self.imagen.url
        return '/static/tienda/img/default-product.png'

    @property
    def stock(self):
        if hasattr(self, 'stock_total'):
            return self.stock_total
        return sum(inv.stock for inv in self.inventarios.all())
    
    @property
    def tiene_stock(self):
        return self.stock > 0


# RF06 - Inventario por talla y color
class Inventario(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="inventarios"
    )
    talla = models.ForeignKey(Talla, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'talla', 'color')
        verbose_name_plural = "Inventarios"

    def __str__(self):
        return f"{self.producto} - {self.talla} - {self.color}"

    # ✅ Estado REAL por variante
    @property
    def estado_stock(self):
        if self.stock == 0:
            return "out"
        elif self.stock <= 5:
            return "last"
        return "in"



# RF07-RF08-RF09 - Movimientos
class Movimiento(models.Model):

    TIPOS = [
        ("ENTRADA", "Entrada"),
        ("SALIDA", "Salida"),
    ]

    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        related_name="movimientos"
    )

    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    observacion = models.CharField(max_length=150, blank=True)

    def save(self, *args, **kwargs):

        if self.pk:
            raise ValidationError("No se permite modificar movimientos")

        if self.tipo == "SALIDA" and self.inventario.stock < self.cantidad:
            raise ValidationError("Stock insuficiente")

        if self.tipo == "ENTRADA":
            self.inventario.stock += self.cantidad
        else:
            self.inventario.stock -= self.cantidad

        self.inventario.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.cantidad}"


# --- E-COMMERCE MODELS ---

class PerfilCliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Carrito {self.id}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variante = models.ForeignKey(Inventario, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.producto.precio_final * self.cantidad

class Orden(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_completo = models.CharField(max_length=200)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    transaccion_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Orden {self.id} - {self.nombre_completo}"

class OrdenItem(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    variante = models.ForeignKey(Inventario, on_delete=models.SET_NULL, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Orden {self.orden.id})"

