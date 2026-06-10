import json
import os

ARCHIVO_DATOS = "datos.json"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
        
    else:
        return[]
def guardar_datos(movimientos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
        json.dump(movimientos, archivo, indent=4, ensure_ascii=False)
def mostrar_menu():
 print("\n====GESTOR DE GASTOS ====")
 print("1. Añadir ingreso")
 print("2. Añadir gasto")
 print("3. Ver movimiento")
 print("4. Ver resumen")
 print("5. Salir")
def añadir_movimiento(movimientos, tipo):
    descripcion=input("Descripción: ")
    cantidad= float(input("Cantidad:"))
    categoria= input("Categoría: ")
    movimiento={
        "tipo": tipo,
        "descripcion": descripcion,
        "cantidad": cantidad,
        "categoria": categoria
    }
    movimientos.append(movimiento)
    guardar_datos(movimientos)
    print("Movimiento guardado correctamente")
def ver_movimientos(movimientos):
    if len(movimientos)== 0:
        print("No hay movimientos guardados.")
    else:
        print("\n==== MOVIMIENTOS ====")
        for movimiento in movimientos:
            print("----------------------")
            print("Tipo: ", movimiento["tipo"])
            print("Descripcion: ", movimiento["descripcion"])
            print("Cantidad: ", movimiento["cantidad"])
            print("Categoria: ", movimiento["categoria"])
def ver_resumen(movimientos):
    ingresos= 0
    gastos= 0
    for movimiento in movimientos:
     if movimiento["tipo"] == "ingreso":
      ingresos= ingresos + movimiento["cantidad"]
     elif movimiento["tipo"]== "gasto":
        gastos= gastos + movimiento["cantidad"]
    balance = ingresos - gastos

    print("\n==== RESUMEN ====")
    print("Ingresos totales: ", ingresos, "€")
    print("Gastos totales: ", gastos, "€")
    print("Balance actual: ", balance, "€")

def main():
   movimientos= cargar_datos()
   opcion=""
   while opcion !="5":
      mostrar_menu()
      opcion=input("Elige una opción: ")

      if opcion=="1":
         añadir_movimiento(movimientos, "ingreso")
      elif opcion=="2":
          añadir_movimiento(movimientos, "gasto")
      elif opcion=="3":
          ver_movimientos(movimientos) 
      elif opcion=="4":
          ver_resumen(movimientos)
      elif opcion=="5":
          print("Saliendo del programa...")
      else:
          print("Opción no válida.")
main()
         


    

        
