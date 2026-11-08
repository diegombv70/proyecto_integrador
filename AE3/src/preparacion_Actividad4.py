"""
Funciones de transformacion, enriquecimiento y resultados - AE3 (Actividad 4).

- perfil_calidad: filas, tipos y nulos de un DataFrame (comparar antes/despues).
- transformar: corrige tipos, trata faltantes y normaliza nombres y categorias.
- enriquecer: agrega variables calculadas para responder las preguntas.
- tabla_tasa: tasa de cancelacion por segmento (tabla de resultados).
- ResumenDescriptivo: genera el .txt descriptivo del DataFrame final.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- reglas
RENOMBRAR = {
    "customerID": "id_cliente", "gender": "genero", "SeniorCitizen": "adulto_mayor",
    "Partner": "tiene_pareja", "Dependents": "tiene_dependientes",
    "tenure": "antiguedad_meses", "PhoneService": "servicio_telefonico",
    "MultipleLines": "lineas_multiples", "InternetService": "servicio_internet",
    "OnlineSecurity": "seguridad_en_linea", "OnlineBackup": "respaldo_en_linea",
    "DeviceProtection": "proteccion_dispositivos", "TechSupport": "soporte_tecnico",
    "StreamingTV": "streaming_tv", "StreamingMovies": "streaming_peliculas",
    "Contract": "tipo_contrato", "PaperlessBilling": "factura_electronica",
    "PaymentMethod": "metodo_pago", "MonthlyCharges": "cargo_mensual",
    "TotalCharges": "cargo_total", "Churn": "cancelo",
}

TRADUCIR = {
    "Yes": "Sí", "No": "No", "Female": "Femenino", "Male": "Masculino",
    "No internet service": "Sin internet", "No phone service": "Sin teléfono",
    "DSL": "DSL", "Fiber optic": "Fibra óptica",
    "Month-to-month": "Mes a mes", "One year": "Un año", "Two year": "Dos años",
    "Electronic check": "Cheque electrónico", "Mailed check": "Cheque por correo",
    "Bank transfer (automatic)": "Transferencia bancaria (automática)",
    "Credit card (automatic)": "Tarjeta de crédito (automática)",
}

ADICIONALES = ["seguridad_en_linea", "respaldo_en_linea", "proteccion_dispositivos",
               "soporte_tecnico", "streaming_tv", "streaming_peliculas"]

ORDEN = {
    "tipo_contrato": ["Mes a mes", "Un año", "Dos años"],
    "servicio_internet": ["DSL", "Fibra óptica", "Sin internet"],
    "rango_antiguedad": ["0-12 meses", "13-24 meses", "25-48 meses", "49-72 meses"],
    "rango_cargo_mensual": ["Bajo (<35)", "Medio (35-70)", "Alto (70-90)", "Muy alto (>=90)"],
    "rango_servicios_adicionales": ["0", "1-2", "3-4", "5-6"],
    "tipo_servicio": ["Solo teléfono", "Solo internet", "Teléfono e internet"],
}


def _es_texto(serie: pd.Series) -> bool:
    return pd.api.types.is_object_dtype(serie) or pd.api.types.is_string_dtype(serie)


# ---------------------------------------------------------------- calidad
def perfil_calidad(df: pd.DataFrame) -> pd.DataFrame:
    """Tipo, nulos, textos vacios y valores unicos por columna."""
    vacios = {c: int(df[c].astype(str).str.strip().eq("").sum()) if _es_texto(df[c]) else 0
              for c in df.columns}
    return pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isnull().sum(),
        "textos_vacios": pd.Series(vacios),
        "valores_unicos": df.nunique(),
    })


# ---------------------------------------------------------------- transformacion
def transformar(df_original: pd.DataFrame):
    """Devuelve (df_transformado, registro_de_cambios). No modifica el original."""
    df = df_original.copy()
    log = []

    # 1. Espacios sobrantes en textos
    texto = [c for c in df.columns if _es_texto(df[c])]
    con_espacios = int(sum((df[c] != df[c].str.strip()).sum() for c in texto))
    for c in texto:
        df[c] = df[c].str.strip()
    log.append(("Quitar espacios en columnas de texto", con_espacios))

    # 2. TotalCharges: texto -> numero. Vacios = clientes con tenure 0 -> 0
    vacios = df["TotalCharges"].eq("")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].replace("", np.nan))
    assert (df.loc[vacios, "tenure"] == 0).all(), "Hay vacios con antiguedad > 0"
    df.loc[vacios, "TotalCharges"] = 0.0
    log.append(("TotalCharges a numero; vacios (tenure = 0) reemplazados por 0", int(vacios.sum())))

    # 3. SeniorCitizen 0/1 -> No/Sí
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    log.append(("SeniorCitizen 0/1 convertido a No/Sí", len(df)))

    # 4. Normalizar categorias (espanol) y nombres de columnas
    categoricas = [c for c in df.columns if _es_texto(df[c]) and c != "customerID"]
    for c in categoricas:
        sin_regla = set(df[c].unique()) - set(TRADUCIR)
        assert not sin_regla, f"{c}: categorias sin regla {sin_regla}"
        df[c] = df[c].map(TRADUCIR)
    # En InternetService "No" significa "sin servicio de internet" (igual que en los adicionales)
    df["InternetService"] = df["InternetService"].replace("No", "Sin internet")
    log.append((f"Categorias traducidas al espanol ({len(categoricas)} columnas)", len(df)))
    df = df.rename(columns=RENOMBRAR)
    log.append(("Columnas renombradas a espanol snake_case", df.shape[1]))

    # 5. Tipos finales
    for c in [RENOMBRAR[c] for c in categoricas]:
        orden = ORDEN.get(c)
        df[c] = pd.Categorical(df[c], categories=orden, ordered=orden is not None) \
            if orden else df[c].astype("category")
    df["id_cliente"] = df["id_cliente"].astype("string")
    log.append(("Columnas categoricas convertidas a tipo category", len(categoricas)))

    registro = pd.DataFrame(log, columns=["transformacion", "registros_o_columnas_afectados"])
    return df, registro


def controles_calidad(df: pd.DataFrame) -> pd.DataFrame:
    """Controles sobre el DataFrame transformado. Cuenta registros con problema."""
    sin_tel = df["servicio_telefonico"] == "No"
    sin_int = df["servicio_internet"] == "Sin internet"
    ratio = df["cargo_total"] / (df["cargo_mensual"] * df["antiguedad_meses"]).replace(0, np.nan)
    controles = {
        "id_cliente duplicado": df["id_cliente"].duplicated().sum(),
        "filas duplicadas completas": df.duplicated().sum(),
        "filas iguales salvo id_cliente (clientes distintos, se conservan)":
            df.drop(columns="id_cliente").duplicated().sum(),
        "valores nulos (total)": df.isnull().sum().sum(),
        "antiguedad_meses fuera de 0-72": (~df["antiguedad_meses"].between(0, 72)).sum(),
        "cargo_mensual <= 0": (df["cargo_mensual"] <= 0).sum(),
        "cargo_total < 0": (df["cargo_total"] < 0).sum(),
        "lineas_multiples incoherente con servicio_telefonico":
            ((df["lineas_multiples"] == "Sin teléfono") != sin_tel).sum(),
        "servicios adicionales incoherentes con servicio_internet":
            sum(((df[c] == "Sin internet") != sin_int).sum() for c in ADICIONALES),
        "cargo_total / (cargo_mensual x antiguedad) fuera de 0,5-2":
            (~ratio.dropna().between(0.5, 2)).sum(),
    }
    tabla = pd.DataFrame({"control": controles.keys(),
                          "registros_con_problema": [int(v) for v in controles.values()]})
    tabla["resultado"] = np.where(tabla["registros_con_problema"].eq(0), "OK", "Revisar")
    tabla.loc[tabla["control"].str.startswith("filas iguales"), "resultado"] = "Informativo"
    return tabla


# ---------------------------------------------------------------- enriquecimiento
def enriquecer(df_t: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables derivadas. No cambia la cantidad de filas."""
    df = df_t.copy()
    df["cancelo_flag"] = (df["cancelo"] == "Sí").astype(int)
    df["rango_antiguedad"] = pd.cut(df["antiguedad_meses"], bins=[-1, 12, 24, 48, 72],
                                    labels=ORDEN["rango_antiguedad"], ordered=True)
    df["rango_cargo_mensual"] = pd.cut(df["cargo_mensual"], bins=[0, 35, 70, 90, np.inf],
                                       right=False, labels=ORDEN["rango_cargo_mensual"], ordered=True)
    tel = df["servicio_telefonico"] == "Sí"
    net = df["servicio_internet"] != "Sin internet"
    df["tipo_servicio"] = pd.Categorical(
        np.select([tel & net, net], ["Teléfono e internet", "Solo internet"], "Solo teléfono"),
        categories=ORDEN["tipo_servicio"], ordered=True)
    df["n_servicios_adicionales"] = (df[ADICIONALES] == "Sí").sum(axis=1).astype(int)
    df["rango_servicios_adicionales"] = pd.cut(df["n_servicios_adicionales"], bins=[-1, 0, 2, 4, 6],
                                               labels=ORDEN["rango_servicios_adicionales"], ordered=True)
    df["pago_automatico"] = pd.Categorical(
        np.where(df["metodo_pago"].astype(str).str.contains("automática"), "Sí", "No"))
    df["tiene_familia"] = pd.Categorical(
        np.where((df["tiene_pareja"] == "Sí") | (df["tiene_dependientes"] == "Sí"), "Sí", "No"))
    df["cargo_mensual_perdido"] = (df["cargo_mensual"] * df["cancelo_flag"]).round(2)
    assert len(df) == len(df_t)
    return df


# ---------------------------------------------------------------- resultados
def tabla_tasa(df: pd.DataFrame, variables, total_df: pd.DataFrame = None) -> pd.DataFrame:
    """Tasa de cancelacion por categoria de cada variable (formato largo)."""
    total_df = df if total_df is None else total_df
    tasa_global = total_df["cancelo_flag"].mean() * 100
    total_clientes, total_cancel = len(total_df), total_df["cancelo_flag"].sum()
    total_perdido = total_df["cargo_mensual_perdido"].sum()
    partes = []
    for var in ([variables] if isinstance(variables, str) else variables):
        g = (df.groupby(var, observed=True)
               .agg(clientes=("id_cliente", "count"), cancelaciones=("cancelo_flag", "sum"),
                    cargo_mensual_promedio=("cargo_mensual", "mean"),
                    cargo_mensual_perdido=("cargo_mensual_perdido", "sum"))
               .reset_index().rename(columns={var: "segmento"}))
        g.insert(0, "variable", var)
        g["segmento"] = g["segmento"].astype(str)
        partes.append(g)
    t = pd.concat(partes, ignore_index=True)
    t["tasa_cancelacion_pct"] = t["cancelaciones"] / t["clientes"] * 100
    t["diferencia_vs_global_pp"] = t["tasa_cancelacion_pct"] - tasa_global
    t["participacion_clientes_pct"] = t["clientes"] / total_clientes * 100
    t["participacion_cancelaciones_pct"] = t["cancelaciones"] / total_cancel * 100
    t["participacion_cargo_perdido_pct"] = t["cargo_mensual_perdido"] / total_perdido * 100
    columnas = ["variable", "segmento", "clientes", "cancelaciones", "tasa_cancelacion_pct",
                "diferencia_vs_global_pp", "participacion_clientes_pct",
                "participacion_cancelaciones_pct", "cargo_mensual_promedio",
                "cargo_mensual_perdido", "participacion_cargo_perdido_pct"]
    return t[columnas].round(2)


def validar_tabla(t: pd.DataFrame, df: pd.DataFrame) -> None:
    """Cada variable debe sumar el total de clientes, cancelaciones y 100 %."""
    for var, g in t.groupby("variable"):
        assert g["clientes"].sum() == len(df), var
        assert g["cancelaciones"].sum() == df["cancelo_flag"].sum(), var
        assert abs(g["participacion_clientes_pct"].sum() - 100) < 0.1, var
        assert abs(g["participacion_cancelaciones_pct"].sum() - 100) < 0.1, var


# ---------------------------------------------------------------- resumen .txt
class ResumenDescriptivo:
    """Genera el resumen descriptivo .txt del DataFrame final."""

    SEP = "=" * 78

    def __init__(self, df: pd.DataFrame, titulo: str, procedencia: dict = None,
                 registro: pd.DataFrame = None):
        self.df, self.titulo = df, titulo
        self.procedencia = procedencia or {}
        self.registro = registro

    def construir(self) -> str:
        df = self.df
        num = df.select_dtypes(include="number")
        cat = df.select_dtypes(include=["category", "object", "string"]).drop(
            columns=["id_cliente"], errors="ignore")
        ancho = max([len(k) for k in self.procedencia] or [0])
        frecuencias = "\n\n".join(
            f"{c}:\n" + (df[c].value_counts().to_frame("clientes")
                         .assign(porcentaje=lambda x: (x["clientes"] / len(df) * 100).round(2))
                         .to_string())
            for c in cat.columns)
        secciones = [
            ("1. Procedencia", "\n".join(f"{k.ljust(ancho)} : {v}" for k, v in self.procedencia.items())),
            ("2. Dimensiones", f"Filas: {df.shape[0]}\nColumnas: {df.shape[1]}"),
            ("3. Columnas y tipos de datos", perfil_calidad(df)[["tipo", "valores_unicos"]].to_string()),
            ("4. Valores nulos por columna",
             f"Total de valores nulos: {int(df.isnull().sum().sum())}\n"
             + df.isnull().sum().to_frame("nulos").to_string()),
            ("5. Estadisticas descriptivas (variables numericas)", num.describe().T.round(2).to_string()),
            ("6. Frecuencias (variables categoricas)", frecuencias),
            ("7. Indicador principal",
             f"Clientes: {len(df)}\nCancelaciones: {int(df['cancelo_flag'].sum())}\n"
             f"Tasa de cancelacion global: {df['cancelo_flag'].mean() * 100:.2f} %"),
        ]
        if self.registro is not None:
            secciones.append(("8. Transformaciones aplicadas", self.registro.to_string(index=False)))
        secciones.append(("9. Muestra (primeras 5 filas)", df.head().to_string()))
        lineas = [self.SEP, self.titulo.upper(), f"Generado: {datetime.now():%Y-%m-%d %H:%M:%S}", self.SEP]
        for nombre, contenido in secciones:
            lineas += ["", nombre, "-" * len(nombre), contenido]
        return "\n".join(lineas + ["", self.SEP])

    def guardar(self, ruta) -> Path:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(self.construir(), encoding="utf-8")
        return ruta
