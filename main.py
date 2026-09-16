import sys
import numpy
import pandas
from dotenv import load_dotenv

print("Python utilisé :")
print(sys.executable)

print("\nVersions :")
print("NumPy :", numpy.__version__)
print("Pandas :", pandas.__version__)

load_dotenv()

print("\n✅ Environnement RAG opérationnel !")