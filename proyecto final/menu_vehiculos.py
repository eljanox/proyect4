# Importamos las bibliotecas necesarias
import pymongo  # Para conectarse a MongoDB
from bson import ObjectId  # Para trabajar con IDs en MongoDB
from datetime import datetime  # Para obtener el año actual

# Clase para gestionar la conexión a MongoDB
class Conexion:
    def __init__(self, uri="mongodb+srv://taller:taller@cluster0.tzztwfj.mongodb.net/", db_name="TallerVehiculosDB"):
        try:
            self.client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            self.client.server_info()  # Verifica conexión
            self.estado = True
        except pymongo.errors.ServerSelectionTimeoutError as error:
            print("❌ Error de conexión:", error)
            self.estado = False

# Crear instancia de conexión
conexion = Conexion()

# Verificamos si la conexión fue exitosa
if conexion.estado:
    print("✅ Conexión exitosa a MongoDB Atlas")
else:
    print("❌ No se pudo conectar a MongoDB")

# Clase del menú de vehículos
class Menu:
    def __init__(self):
        while True:
            print("\n--- MENÚ DE VEHÍCULOS ---")
            print("1. Listar vehículos")
            print("2. Buscar por marca")
            print("3. Insertar vehículo")
            print("4. Insertar varios vehículos")
            print("5. Actualizar estado si cumple condición")
            print("6. Eliminar vehículos antiguos (>10 años)")
            print("7. Mostrar resumen (marca, modelo, km)")
            print("8. Salir")

            opcion = input("Seleccione una opción: ").strip()

            if opcion == "1":
                self.listar_vehiculos()
            elif opcion == "2":
                self.buscar_por_marca()
            elif opcion == "3":
                self.insertar_vehiculo()
            elif opcion == "4":
                self.insertar_varios()
            elif opcion == "5":
                self.actualizar_estado()
            elif opcion == "6":
                self.eliminar_antiguos()
            elif opcion == "7":
                self.mostrar_resumen()
            elif opcion == "8":
                print("👋 Saliendo del programa.")
                break
            else:
                print("❌ Opción no válida.")

    def listar_vehiculos(self):
        print("\n🚗 Listado de vehículos:")
        for vehiculo in conexion.db.vehiculos.find():
            print(vehiculo)

    def buscar_por_marca(self):
        marca = input("🔍 Ingrese la marca del vehículo: ").strip()
        resultados = conexion.db.vehiculos.find({
            "vehiculo.marca": { "$regex": f"^{marca}$", "$options": "i" }
        })
        encontrados = False
        for v in resultados:
            print(v)
            encontrados = True
        if not encontrados:
            print("❌ No se encontraron vehículos con esa marca.")

    def insertar_vehiculo(self):
        try:
            nuevo = {
                "vehiculo": {
                    "marca": input("Marca: "),
                    "modelo": input("Modelo: "),
                    "anio": int(input("Año: ")),
                    "kilometraje": int(input("Kilometraje: "))
                },
                "estadoActual": {
                    "estadoGeneral": input("Estado general (Bueno/Regular/Malo): ")
                }
            }
            conexion.db.vehiculos.insert_one(nuevo)
            print("✅ Vehículo insertado exitosamente.")
        except ValueError:
            print("❌ Error: los campos año y kilometraje deben ser números.")

    def insertar_varios(self):
        try:
            cantidad = int(input("¿Cuántos vehículos desea ingresar?: "))
            lista = []
            for i in range(cantidad):
                print(f"\nVehículo {i + 1}")
                vehiculo = {
                    "vehiculo": {
                        "marca": input("Marca: "),
                        "modelo": input("Modelo: "),
                        "anio": int(input("Año: ")),
                        "kilometraje": int(input("Kilometraje: "))
                    },
                    "estadoActual": {
                        "estadoGeneral": input("Estado general (Bueno/Regular/Malo): ")
                    }
                }
                lista.append(vehiculo)
            if lista:
                conexion.db.vehiculos.insert_many(lista)
                print(f"✅ Se insertaron {len(lista)} vehículos.")
        except ValueError:
            print("❌ Error: los campos año y kilometraje deben ser números.")

    def actualizar_estado(self):
        id = input("🛠️ Ingrese el ID del vehículo a actualizar: ").strip()
        try:
            vehiculo = conexion.db.vehiculos.find_one({"_id": ObjectId(id)})
            if not vehiculo:
                print("❌ Vehículo no encontrado.")
                return
            km = vehiculo["vehiculo"]["kilometraje"]
            estado = vehiculo["estadoActual"]["estadoGeneral"]
            if km < 90000 and estado == "Regular":
                conexion.db.vehiculos.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": {"estadoActual.estadoGeneral": "Bueno"}}
                )
                print("✅ Estado actualizado a Bueno.")
            else:
                print("ℹ️ No cumple condición para actualizar.")
        except Exception as e:
            print("❌ Error al actualizar:", e)

    def eliminar_antiguos(self):
        anio_actual = datetime.now().year
        resultado = conexion.db.vehiculos.delete_many({
            "vehiculo.anio": { "$lt": anio_actual - 10 }
        })
        print(f"🗑️ Vehículos eliminados: {resultado.deleted_count}")

    def mostrar_resumen(self):
        print("\n📋 Resumen de vehículos:")
        resumen = conexion.db.vehiculos.find({}, {
            "vehiculo.marca": 1,
            "vehiculo.modelo": 1,
            "vehiculo.kilometraje": 1,
            "_id": 0
        })
        for v in resumen:
            print(v)

# Ejecutar menú si hay conexión
if conexion.estado:
    Menu()