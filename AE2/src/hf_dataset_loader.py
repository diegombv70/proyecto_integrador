"""
Modulo de carga de datos desde Hugging Face Datasets.

Contiene la clase HFDatasetLoader, responsable de conectarse a Hugging Face,
descargar un dataset a partir de su identificador y devolverlo como un
DataFrame de pandas.
"""

from typing import Optional

import pandas as pd
from datasets import load_dataset, get_dataset_split_names


class HFDatasetLoader:
    """Obtiene un dataset de Hugging Face y lo convierte en DataFrame de pandas.

    Parametros
    ----------
    dataset_id : str
        Identificador del dataset en Hugging Face (por ejemplo, "scikit-learn/churn-prediction").
    split : str, opcional
        Particion que se desea cargar ("train", "test", "validation", ...).
        Por defecto se usa "train".
    config_name : str, opcional
        Nombre de la configuracion/subconjunto, para datasets que lo requieran.
    revision : str, opcional
        Commit o rama del repositorio del dataset. Fijarla garantiza que
        siempre se descargue la misma version de los datos.

    Ejemplo
    -------
    >>> loader = HFDatasetLoader("scikit-learn/churn-prediction", split="train")
    >>> df = loader.load()
    """

    def __init__(self, dataset_id: str, split: str = "train",
                 config_name: Optional[str] = None,
                 revision: Optional[str] = None):
        if not dataset_id or not isinstance(dataset_id, str):
            raise ValueError("Debe indicar un identificador de dataset valido.")
        self.dataset_id = dataset_id
        self.split = split
        self.config_name = config_name
        self.revision = revision
        self._dataset = None
        self._dataframe: Optional[pd.DataFrame] = None

    def available_splits(self) -> list:
        """Devuelve la lista de splits disponibles para el dataset."""
        return get_dataset_split_names(self.dataset_id, self.config_name,
                                       revision=self.revision)

    def _connect(self):
        """Se conecta a Hugging Face y descarga el split solicitado."""
        try:
            self._dataset = load_dataset(
                self.dataset_id, self.config_name, split=self.split,
                revision=self.revision
            )
        except Exception as error:
            raise RuntimeError(
                f"No fue posible cargar '{self.dataset_id}' "
                f"(split='{self.split}'): {error}"
            ) from error
        return self._dataset

    def load(self) -> pd.DataFrame:
        """Carga el dataset y lo devuelve como un DataFrame de pandas."""
        if self._dataset is None:
            self._connect()
        self._dataframe = self._dataset.to_pandas()
        return self._dataframe

    def get_dataframe(self) -> pd.DataFrame:
        """Devuelve el DataFrame ya cargado, cargandolo si aun no existe."""
        if self._dataframe is None:
            return self.load()
        return self._dataframe

    def __repr__(self) -> str:
        return (f"HFDatasetLoader(dataset_id='{self.dataset_id}', "
                f"split='{self.split}', config_name={self.config_name!r}, "
                f"revision={self.revision!r})")
