from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer
import io
print("[DEBUG] Запуск visuals.py")


def plot_circuit() -> bytes:
    """Генерирует изображение квантовой схемы"""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    buf = io.BytesIO()
    circuit_drawer(qc, output="mpl").savefig(buf, format="png")
    buf.seek(0)
    return buf.getvalue()