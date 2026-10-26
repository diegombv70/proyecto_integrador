"""
Modulo de resumen de DataFrames.

Contiene la clase DatasetSummarizer, que recibe un DataFrame de pandas,
construye un resumen descriptivo de su contenido y lo exporta a un archivo .txt.
Esta clase no se conecta a ninguna fuente: solo trabaja con los datos recibidos.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


class DatasetSummarizer:
    """Resume un DataFrame y guarda el resumen en un archivo de texto.

    Parametros
    ----------
    dataframe : pd.DataFrame
        Datos que se van a resumir.
    title : str, opcional
        Titulo que encabeza el resumen (por ejemplo, el nombre del dataset).
    source : dict, opcional
        Metadatos de procedencia que se imprimen al inicio del resumen
        (identificador, split, revision, muestra, etc.).

    Ejemplo
    -------
    >>> summarizer = DatasetSummarizer(df, title="Telco Churn",
    ...                                source={"Identificador": "scikit-learn/churn-prediction"})
    >>> summarizer.save_txt("AE2/resultados/resumen_dataframe.txt")
    """

    SEPARATOR = "=" * 70

    def __init__(self, dataframe: pd.DataFrame, title: Optional[str] = None,
                 source: Optional[dict] = None):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Se esperaba un DataFrame de pandas.")
        self.df = dataframe
        self.title = title or "Resumen del DataFrame"
        self.source = source or {}

    def source_info(self) -> str:
        """Procedencia del DataFrame: dataset, split, revision y muestra."""
        if not self.source:
            return "Procedencia no indicada."
        width = max(len(key) for key in self.source)
        return "\n".join(f"{key.ljust(width)} : {value}"
                         for key, value in self.source.items())

    def shape_info(self) -> str:
        """Cantidad de filas y columnas."""
        rows, cols = self.df.shape
        return f"Filas: {rows}\nColumnas: {cols}"

    def columns_info(self) -> str:
        """Nombre y tipo de dato de cada columna."""
        info = pd.DataFrame({
            "n": range(1, self.df.shape[1] + 1),
            "columna": self.df.columns,
            "tipo": self.df.dtypes.astype(str).values,
            "valores_unicos": self.df.nunique().values,
        })
        return info.to_string(index=False)

    def nulls_info(self) -> str:
        """Cantidad y porcentaje de valores nulos por columna.

        Ademas de los nulos reconocidos por pandas (NaN/None), cuenta los
        textos vacios o con solo espacios, que pandas no detecta como nulos.
        """
        nulls = self.df.isnull().sum()
        blanks = self.df.apply(
            lambda col: col.astype(str).str.strip().eq("").sum()
            if col.dtype == object else 0
        )
        total = int(nulls.sum())
        pct = (nulls / len(self.df) * 100).round(2) if len(self.df) else nulls
        table = pd.DataFrame({"nulos": nulls, "porcentaje_%": pct,
                              "textos_vacios": blanks})
        header = (f"Total de valores nulos: {total}\n"
                  f"{'El DataFrame NO tiene valores nulos.' if total == 0 else 'El DataFrame tiene valores nulos.'}\n"
                  f"Total de textos vacios (posibles faltantes): {int(blanks.sum())}\n")
        return header + table.to_string()

    def sample_rows(self, n: int = 5) -> str:
        """Primeras filas del DataFrame como muestra."""
        return self.df.head(n).to_string()

    def build_summary(self) -> str:
        """Construye el texto completo del resumen."""
        sections = [
            ("1. Procedencia del dataset", self.source_info()),
            ("2. Dimensiones", self.shape_info()),
            ("3. Columnas y tipos de datos", self.columns_info()),
            ("4. Valores nulos por columna", self.nulls_info()),
            ("5. Muestra de datos (primeras 5 filas)", self.sample_rows()),
        ]
        lines = [
            self.SEPARATOR,
            self.title.upper(),
            f"Generado: {datetime.now():%Y-%m-%d %H:%M:%S}",
            self.SEPARATOR,
        ]
        for name, content in sections:
            lines += ["", name, "-" * len(name), content]
        lines += ["", self.SEPARATOR]
        return "\n".join(lines)

    def save_txt(self, path: str = "resumen_dataframe.txt") -> Path:
        """Guarda el resumen en un archivo .txt (UTF-8) y devuelve su ruta.

        Crea la carpeta si no existe y sobrescribe el archivo en cada llamada.
        """
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.build_summary(), encoding="utf-8")
        return output
