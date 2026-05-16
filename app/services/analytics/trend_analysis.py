# placeholder
def analyze_trend(semester_scores):

    if len(semester_scores) < 2:
        return {
            "trend": "Insufficient Data",
            "growth_percent": 0
        }

    first_score = semester_scores[0]
    last_score = semester_scores[-1]

    growth = ((last_score - first_score) / first_score) * 100

    if growth > 0:
        trend = "Improving"

    elif growth < 0:
        trend = "Declining"

    else:
        trend = "Stable"

    return {
        "trend": trend,
        "growth_percent": round(growth, 2)
    }


if __name__ == "__main__":

    sample_scores = [7.2, 7.8, 8.1, 8.4]

    result = analyze_trend(sample_scores)

    print(result)
