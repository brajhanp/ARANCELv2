# Diccionario de Sinónimos para búsqueda de productos arancelarios
# Agrupa términos equivalentes, variantes regionales y relacionados

SINONIMOS = {
    # BOVINOS Y EQUINOS
    "vaca": ["bovino", "res", "ganado vacuno", "ganado bovino", "toro", "novillo", "becerro", "carne de res"],
    "bovino": ["vaca", "res", "ganado bovino", "ganado vacuno", "toro", "novillo", "becerro"],
    "res": ["vaca", "bovino", "ganado vacuno", "ganado bovino", "toro", "novillo", "becerro", "carne de res"],
    "ganado vacuno": ["vaca", "bovino", "res", "ganado bovino", "toro", "novillo", "becerro"],
    "ganado bovino": ["vaca", "bovino", "res", "ganado vacuno", "toro", "novillo", "becerro"],
    
    "caballo": ["equino", "caballos", "potro", "yegua", "caballo criollo", "équido"],
    "equino": ["caballo", "caballos", "potro", "yegua", "équido"],
    "potro": ["caballo", "equino", "caballos", "yegua"],
    "yegua": ["caballo", "equino", "potro"],
    "équido": ["caballo", "equino", "caballo", "potro", "yegua"],
    
    "toro": ["vaca", "bovino", "res", "ganado vacuno", "animal reproductor"],
    "novillo": ["vaca", "bovino", "res", "ganado vacuno", "becerro"],
    "becerro": ["vaca", "bovino", "res", "novillo", "cría de vacuno"],
    
    # PESCADOS Y MARISCOS
    "pez": ["peces", "pescado", "pez fresco", "pescadilla", "bacalao", "trucha", "salmón", "merluza"],
    "peces": ["pez", "pescado", "pez fresco", "pescadilla", "bacalao", "trucha", "salmón", "merluza"],
    "pescado": ["pez", "peces", "pescado fresco", "pescadilla", "bacalao", "trucha", "salmón", "merluza"],
    "pescadilla": ["pez", "peces", "pescado", "bacalao", "merluza"],
    "bacalao": ["pez", "peces", "pescado", "merluza", "sollo"],
    "trucha": ["pez", "peces", "pescado", "salmón"],
    "salmón": ["pez", "peces", "pescado", "trucha"],
    "merluza": ["pez", "peces", "pescado", "bacalao", "pescadilla"],
    "sollo": ["pez", "peces", "bacalao", "pescado de agua dulce"],
    
    "marisco": ["mariscos", "crustáceo", "camarón", "camarón", "langosta", "cangrejo", "ostra"],
    "mariscos": ["marisco", "crustáceo", "camarón", "langosta", "cangrejo", "ostra"],
    "camarón": ["marisco", "mariscos", "crustáceo", "langostino"],
    "langostino": ["marisco", "mariscos", "camarón", "crustáceo"],
    "langosta": ["marisco", "mariscos", "crustáceo"],
    "cangrejo": ["marisco", "mariscos", "crustáceo"],
    "ostra": ["marisco", "mariscos", "molusco"],
    "mejillón": ["marisco", "mariscos", "molusco"],
    "molusco": ["marisco", "mariscos", "ostra", "mejillón"],
    
    # AVES Y HUEVOS
    "huevo": ["huevos", "ovoproduto", "clara", "yema", "cascara", "huevo de gallina", "huevo de codorniz"],
    "huevos": ["huevo", "ovoproduto", "clara", "yema", "huevo de gallina", "huevo de codorniz"],
    "gallina": ["pollo", "ave", "aves", "gallo", "corral"],
    "pollo": ["gallina", "ave", "aves", "carne de pollo", "pechuga", "muslo", "ala"],
    "ave": ["gallina", "pollo", "aves", "pavo", "pato", "codorniz"],
    "aves": ["ave", "gallina", "pollo", "pavo", "pato", "codorniz"],
    "pavo": ["ave", "aves", "pollo", "gallina"],
    "pato": ["ave", "aves", "pollo", "gallina"],
    "codorniz": ["ave", "aves", "huevo"],
    
    # PORCINOS
    "cerdo": ["porcino", "cerdos", "puerco", "cochino", "lechón", "jamón", "tocino"],
    "porcino": ["cerdo", "cerdos", "puerco", "cochino", "lechón"],
    "puerco": ["cerdo", "porcino", "cochino", "lechón"],
    "cochino": ["cerdo", "porcino", "puerco", "lechón"],
    "lechón": ["cerdo", "porcino", "cría de cerdo"],
    "jamón": ["cerdo", "porcino", "embutido", "carne de cerdo"],
    "tocino": ["cerdo", "porcino", "grasa de cerdo"],
    
    # OVINOS Y CAPRINOS
    "oveja": ["ovino", "ovejas", "borrego", "carnero", "lana", "carne de oveja"],
    "ovino": ["oveja", "ovejas", "borrego", "carnero"],
    "borrego": ["oveja", "ovino", "ovejas", "carnero"],
    "carnero": ["oveja", "ovino", "borrego", "animal reproductor"],
    
    "cabra": ["caprino", "cabras", "chivo", "cabrilla", "leche de cabra"],
    "caprino": ["cabra", "cabras", "chivo"],
    "chivo": ["cabra", "caprino", "macho cabrío"],
    
    # PRODUCTOS LÁCTEOS
    "leche": ["lácteo", "lacteos", "producto lácteo", "leche en polvo", "leche condensada"],
    "lacteo": ["leche", "lacteos", "producto lácteo"],
    "lacteos": ["leche", "lacteo", "producto lácteo"],
    "queso": ["lácteo", "quesería", "queso fresco", "queso curado"],
    "mantequilla": ["lácteo", "manteca", "producto lácteo"],
    "yogur": ["lácteo", "fermentado", "producto lácteo"],
    "crema": ["lácteo", "nata", "producto lácteo"],
    
    # CEREALES Y GRANOS
    "trigo": ["cereal", "grano", "harina de trigo", "trigo candeal", "trigo blando"],
    "maíz": ["cereal", "grano", "choclo", "maíz blanco", "maíz amarillo", "harina de maíz"],
    "arroz": ["cereal", "grano", "arroz blanco", "arroz integral", "arrocero"],
    "cebada": ["cereal", "grano"],
    "avena": ["cereal", "grano"],
    "centeno": ["cereal", "grano"],
    "sorgo": ["cereal", "grano"],
    
    "cereal": ["trigo", "maíz", "arroz", "cebada", "avena", "centeno", "sorgo", "grano"],
    "grano": ["cereal", "trigo", "maíz", "arroz", "cebada", "avena"],
    
    # FRUTAS Y VERDURAS
    "manzana": ["fruta", "pomácea", "manzana roja", "manzana verde"],
    "pera": ["fruta", "pomácea"],
    "uva": ["fruta", "vinífera", "uva de mesa", "uva para vino"],
    "naranja": ["fruta", "cítrico", "citrus"],
    "limón": ["fruta", "cítrico", "citrus", "lima"],
    "plátano": ["fruta", "banana", "banano"],
    "banana": ["fruta", "plátano", "banano"],
    "papaya": ["fruta", "tropical"],
    "mango": ["fruta", "tropical", "mango de exportación"],
    
    "papa": ["tubérculo", "patata", "papa criolla", "papa nativa"],
    "patata": ["papa", "tubérculo"],
    "tubérculo": ["papa", "patata", "yuca", "camote"],
    "yuca": ["tubérculo", "mandioca"],
    "camote": ["tubérculo", "batata"],
    
    "tomate": ["hortalizas", "solanácea", "tomate fresco", "tomate maduro"],
    "lechuga": ["hortalizas", "verdura", "lechuga fresca"],
    "verdura": ["hortalizas", "lechuga", "repollo", "zanahoria"],
    "hortalizas": ["verdura", "tomate", "lechuga", "repollo"],
    "zanahoria": ["hortalizas", "tubérculo", "verdura"],
    "repollo": ["hortalizas", "verdura", "col"],
    "col": ["hortalizas", "repollo", "verdura"],
    
    # PRODUCTOS ESPECIALES
    "miel": ["producto apícola", "apícola", "miel de abeja"],
    "apícola": ["miel", "producto apícola", "abeja"],
    "abeja": ["apícola", "miel", "producto apícola"],
    
    "café": ["cafeto", "grano de café", "café molido", "café instantáneo", "cafetería"],
    "cacao": ["chocolate", "cacao en grano", "pasta de cacao", "cocoa"],
    "chocolate": ["cacao", "producto de cacao", "chocolatería"],
    
    # CARNES Y DERIVADOS
    "carne": ["carnes", "producto cárnico", "carne roja", "carne blanca", "carne fresca"],
    "carnes": ["carne", "producto cárnico"],
    "embutido": ["producto cárnico", "chorizo", "salchicha", "mortadela", "jamón"],
    "chorizo": ["embutido", "producto cárnico"],
    "salchicha": ["embutido", "producto cárnico"],
    "jamón": ["embutido", "producto cárnico", "cerdo"],
    
    # ESPECIAS Y CONDIMENTOS
    "pimienta": ["especia", "condimento", "pimienta negra", "pimienta blanca"],
    "sal": ["condimento", "cloruro de sodio"],
    "ajo": ["condimento", "hortaliza"],
    "cebolla": ["condimento", "hortaliza"],
    "canela": ["especia", "condimento"],
    
    # ACEITES Y GRASAS
    "aceite": ["grasa", "aceite vegetal", "aceite de oliva", "aceite de palma", "aceite de soja"],
    "grasa": ["aceite", "grasa animal", "manteca"],
    "manteca": ["grasa", "producto lácteo", "mantequilla"],
    
    # BEBIDAS
    "vino": ["bebida alcohólica", "vino tinto", "vino blanco", "vino rosado"],
    "cerveza": ["bebida alcohólica", "cervecería"],
    "bebida": ["bebida alcohólica", "bebida sin alcohol", "líquido"],
    "jugo": ["bebida", "zumo", "jugo de fruta"],
    "zumo": ["jugo", "bebida", "zumo de fruta"],
    
    # FLORES Y PLANTAS
    "flor": ["flores", "planta ornamental", "flor cortada", "botánica"],
    "flores": ["flor", "planta ornamental"],
    "rosa": ["flor", "flores", "planta ornamental"],
    "clavel": ["flor", "flores", "planta ornamental"],
    
    # TEXTILES Y FIBRAS
    "lana": ["fibra", "tejido", "oveja", "producto textil"],
    "algodón": ["fibra", "tejido", "producto textil"],
    "seda": ["fibra", "tejido", "producto textil"],
    "fibra": ["lana", "algodón", "seda", "producto textil"],
    
    # MADERAS
    "madera": ["forestal", "madera aserrada", "tabla", "tablón", "leña"],
    "forestal": ["madera", "producto forestal"],
    "tabla": ["madera", "madera aserrada"],
    "leña": ["madera", "combustible"],
}

def obtener_sinonimos(palabra):
    """
    Retorna una lista de sinónimos para una palabra.
    Si la palabra no está en el diccionario, retorna una lista vacía.
    """
    palabra_lower = palabra.lower().strip()
    return SINONIMOS.get(palabra_lower, [])

def expandir_busqueda_con_sinonimos(termino):
    """
    Expande un término de búsqueda incluyendo todos sus sinónimos.
    Retorna una lista de términos a buscar.
    """
    termino_lower = termino.lower().strip()
    terminos = {termino_lower}  # Usar set para evitar duplicados
    
    # Agregar los sinónimos directos
    if termino_lower in SINONIMOS:
        terminos.update(SINONIMOS[termino_lower])
    
    # Búsqueda inversa: si el término es sinónimo de otro, agregar todos los sinónimos de ese
    for palabra_clave, sinonimos_lista in SINONIMOS.items():
        if termino_lower in sinonimos_lista:
            terminos.add(palabra_clave)
            terminos.update(sinonimos_lista)
    
    return list(terminos)

def aplicar_sinonimos_a_query(query):
    """
    Procesa una query de búsqueda para incluir todos los sinónimos de las palabras encontradas.
    Retorna una tupla: (query_original, lista_de_sinonimos_encontrados, query_expandida)
    """
    palabras = query.lower().split()
    sinonimos_encontrados = {}
    todas_las_palabras = set(palabras)
    
    for palabra in palabras:
        if palabra in SINONIMOS:
            sinonimos_encontrados[palabra] = SINONIMOS[palabra]
            todas_las_palabras.update(SINONIMOS[palabra])
    
    return query, sinonimos_encontrados, list(todas_las_palabras)
