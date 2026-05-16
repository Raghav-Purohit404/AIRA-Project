from app.services.analytics.trend_analysis import (
    analyze_trend
)


def test_improving_trend():

    scores = [7.0, 7.5, 8.0, 8.5]

    result = analyze_trend(scores)

    assert result["trend"] == "Improving"


def test_declining_trend():

    scores = [8.5, 8.0, 7.5, 7.0]

    result = analyze_trend(scores)

    assert result["trend"] == "Declining"