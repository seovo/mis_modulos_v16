class Producto:
    """
    Representa un producto con sus atributos.
    """
    def __init__(self, product_sku, name, categ, uom, state):
        """
        Inicializa una nueva instancia de la clase Producto.

        Args:
            product_sku (str): El SKU del producto.
            name (str): El nombre del producto.
            categ (str): La categoría del producto.
            uom (str): La unidad de medida del producto.
            state (str): El estado del producto.
        """
        self.product_sku = product_sku
        self.name = name
        self.categ = categ
        self.uom = uom
        self.state = state

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto Producto.
        """
        return (f"Producto(SKU='{self.product_sku}', Nombre='{self.name}', "
                f"Categoría='{self.categ}', UOM='{self.uom}', Estado='{self.state}')")
