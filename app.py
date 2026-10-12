"""Dashboard Statistik Deskriptif Mahasiswa (Flask + pandas).

Jalankan:
    pip install -r requirements.txt
    python app.py
Lalu buka http://127.0.0.1:5000
"""
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).parent
CSV_FILE = BASE_DIR / "latihan1.csv"

app = Flask(__name__)

df = pd.read_csv(CSV_FILE)
NUMERIC_COLS = [c for c in df.select_dtypes("number").columns if c != "Student_ID"]


def label(col: str) -> str:
    return col.replace("_", " ")


def num(x, nd=2):
    """Bulatkan angka; kembalikan int bila bilangan bulat."""
    x = float(x)
    x = round(x, nd)
    return int(x) if x == int(x) else x


def fmt_edge(v, nd):
    return f"{v:.{nd}f}"


def describe(col: str) -> dict:
    s = df[col].dropna()
    q1, med, q3 = s.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = int(((s < low) | (s > high)).sum())
    skew = float(s.skew())
    mean = float(s.mean())
    std = float(s.std(ddof=1))

    if skew > 0.5:
        shape = "Condong kanan"
    elif skew < -0.5:
        shape = "Condong kiri"
    else:
        shape = "Simetris"

    # histogram 10 bin
    edges = np.linspace(s.min(), s.max(), 11)
    # bin tertutup di kanan (a, b], nilai min masuk bin pertama
    counts = pd.cut(s, bins=edges, include_lowest=True).value_counts(sort=False).values
    nd = 0 if (s.max() - s.min()) >= 100 else 1
    bins = [f"{fmt_edge(edges[i], nd)}-{fmt_edge(edges[i + 1], nd)}" for i in range(10)]

    return {
        "column": col,
        "label": label(col),
        "stats": {
            "mean": num(mean),
            "median": num(med),
            "mode": num(s.mode().iloc[0]),
            "std": num(std),
            "variance": num(s.var(ddof=1)),
            "range": num(s.max() - s.min()),
            "q1": num(q1),
            "q3": num(q3),
            "iqr": num(iqr),
            "skewness": num(skew),
            "cv": num(std / mean * 100, 1) if mean else 0,
            "outliers": outliers,
        },
        "shape": shape,
        "min": num(s.min()),
        "max": num(s.max()),
        "histogram": {"labels": bins, "counts": counts.tolist()},
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    return jsonify(
        {
            "total": int(len(df)),
            "columns": int(df.shape[1]),
            "avg_exam": num(df["Exam_Score"].mean()),
            "avg_study": num(df["Study_Hours"].mean()),
            "variables": [{"value": c, "label": label(c)} for c in NUMERIC_COLS],
        }
    )


@app.route("/api/variable/<col>")
def variable(col):
    if col not in NUMERIC_COLS:
        return jsonify({"error": "Kolom tidak ditemukan"}), 404
    return jsonify(describe(col))


@app.route("/api/gender")
def gender():
    counts = df["Gender"].value_counts().sort_index()
    avg = df.groupby("Gender")["Exam_Score"].mean().round(2).reindex(counts.index)
    return jsonify(
        {
            "labels": counts.index.tolist(),
            "counts": counts.values.tolist(),
            "avg_exam": avg.values.tolist(),
        }
    )


@app.route("/api/scatter")
def scatter():
    x = request.args.get("x", "Study_Hours")
    y = request.args.get("y", "Exam_Score")
    if x not in NUMERIC_COLS or y not in NUMERIC_COLS:
        return jsonify({"error": "Kolom tidak ditemukan"}), 404

    d = df[[x, y]].dropna()
    r = float(d[x].corr(d[y])) if x != y else 1.0
    slope, intercept = np.polyfit(d[x], d[y], 1) if x != y else (1.0, 0.0)
    xs = [float(d[x].min()), float(d[x].max())]
    line = [{"x": v, "y": float(slope * v + intercept)} for v in xs]

    if abs(r) >= 0.7:
        strength = "kuat"
    elif abs(r) >= 0.4:
        strength = "sedang"
    else:
        strength = "lemah"
    direction = "positif" if r >= 0 else "negatif"

    return jsonify(
        {
            "points": [{"x": float(a), "y": float(b)} for a, b in zip(d[x], d[y])],
            "line": line,
            "r": round(r, 3),
            "r2": round(r * r, 3),
            "slope": round(float(slope), 3),
            "intercept": round(float(intercept), 3),
            "interpretation": f"Korelasi {strength} {direction}",
            "x_label": label(x),
            "y_label": label(y),
        }
    )


@app.route("/api/correlation")
def correlation():
    c = df[NUMERIC_COLS].corr()["Exam_Score"].drop("Exam_Score")
    c = c.reindex(c.abs().sort_values(ascending=False).index)
    return jsonify({"labels": [label(i) for i in c.index], "values": c.round(2).tolist()})


@app.route("/api/matrix")
def matrix():
    m = df[NUMERIC_COLS].corr().round(2)
    return jsonify({"labels": [label(c) for c in m.columns], "values": m.values.tolist()})


@app.route("/api/segments")
def segments():
    bins = [(0, 60, "< 60", True), (60, 70, "60-69", False), (70, 80, "70-79", False), (80, 101, ">= 80", False)]
    return jsonify(
        [
            {"label": lb, "count": int(df["Exam_Score"].between(lo, hi, inclusive="left").sum()), "risk": rk}
            for lo, hi, lb, rk in bins
        ]
    )


if __name__ == "__main__":
    app.run(debug=True)
