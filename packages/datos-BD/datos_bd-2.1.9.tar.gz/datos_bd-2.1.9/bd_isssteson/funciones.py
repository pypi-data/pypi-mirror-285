from .encriptaciones import decrypt, encrypt
from .globales import *


## Retornar servidores
def servidores():
    """ Función que retorna los Servidores Disponibles en la Librería
    
    Returns:
        [Tupla]: [Servidores disponibles para la Librería]
    """
    return (encrypt(servidor1,llave),encrypt(servidor2,llave))
    


## Retornar las bases de datos disponibles para la Librería
def bases_d_datos(servidor):
    """AI is creating summary for bases_d_datos

    Args:
        servidor ([Tupla]): [description]

    Returns:
        [Tupla]: [Listado de Bases disponibles en la Librería según servidor seleccionado]
    """
    ## Cargar todos los servidores disponibles en la tupla
    serv = servidores()

    if decrypt(servidor,llave).decode("utf-8") == decrypt(serv[0],llave).decode("utf-8"):
        return (encrypt(S1_catalogo01,llave),encrypt(S1_catalogo02,llave),encrypt(S1_catalogo03,llave))
    elif decrypt(servidor,llave).decode("utf-8") == decrypt(serv[1],llave).decode("utf-8"):
        return (encrypt(S2_catalogo01,llave),encrypt(S2_catalogo02,llave),None)
    else:
        return (None,None,None)
        #return None


## Retornar los Datos para la Conexión dependiedo del Servidor
def DatosServidor(args):
    """Función para Retornar los parámetros para conexión a Base de Datos, según servidor

    Args:
        args ([Tupla]): [Servidor, Base de Datos]

    Returns:
        [Tupla]: [Servidor, Base de Datos, Usuario, Contraseña]
    """
    # Obtener Tupla con los servidores 
    serv = servidores()

    if decrypt(args[0],llave).decode("utf-8") == decrypt(serv[0],llave).decode("utf-8"):
        cat = bases_d_datos(serv[0])
        if decrypt(args[1], llave).decode("utf-8") == decrypt(cat[0], llave).decode("utf-8"):
            return (serv[0],cat[0],encrypt(sql_usuario01,llave),encrypt(U1_password,llave))
        elif decrypt(args[1],llave).decode("utf-8") == decrypt(cat[1],llave).decode("utf-8"):
            return (serv[0],cat[1],encrypt(sql_usuario01,llave),encrypt(U1_password,llave))
        elif decrypt(args[1],llave).decode("utf-8") == decrypt(cat[2],llave).decode("utf-8"):
            return (serv[0],cat[2],encrypt(sql_usuario01,llave),encrypt(U1_password,llave))
        else:
            return None
    elif decrypt(args[0],llave).decode("utf-8") == decrypt(serv[1],llave).decode("utf-8"):
        cat = bases_d_datos(serv[1])
        if decrypt(args[1],llave).decode("utf-8") == decrypt(cat[0],llave).decode("utf-8"):
            return (serv[1],cat[0],encrypt(sql_usuario01,llave),encrypt(U1_password,llave))
        elif args[1] == cat[1]:
            return (serv[1],cat[1],encrypt(sql_usuario01,llave),encrypt(U1_password,llave))
        else:
            return None
    else:
        return None
    

