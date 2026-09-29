# AQUASHIELD

**AQUASHIELD — Predict. Prevent. Preserve Every Drop.**

AQUASHIELD is an AI-powered water intelligence platform built to help apartment communities conserve water by leveraging right Google Cloud services like BigQuery, BigQuery ML, Gemini, and hosted on the Google Cloud Run platform.

The solution combines water-consumption analytics, machine-learning-based forecasting, deterministic risk assessment, and Gemini-powered contextual recommendations to convert raw water data into practical operational intelligence.



---

## Why AQUASHIELD?

Every drop of water matters.

A small unnoticed leak in a single apartment community can result in thousands of litres of water being wasted. When similar issues occur across hundreds or thousands of residential and commercial communities, the cumulative impact can become significant.

At the same time, apartment facility teams often need to manage:

* Unexpected increases in water consumption
* Leakage or abnormal usage
* Declining tank levels
* Limited municipal water supply
* Tanker dependency
* Potential water shortages
* Conservation opportunities

AQUASHIELD brings these signals together into a single intelligent dashboard so that facility managers can quickly understand:

**Is there a problem? What kind of problem is it? What action should be taken next?**

---

## Live Prototype

AQUASHIELD is deployed on Google Cloud Run:

```text
https://aquashield-334593224319.asia-south1.run.app
```

---

## Key Capabilities

### Water Consumption Intelligence

AQUASHIELD compares actual daily water consumption against an expected consumption baseline generated using a BigQuery ML model.

Significant deviations from expected consumption can indicate abnormal water usage and trigger increased leak risk.

---

### Leak Risk Detection

Leak risk is calculated based on the difference between actual and predicted water consumption.

The application classifies conditions into:

* **LOW** — Consumption is within the expected operating range.
* **MEDIUM** — Consumption is moderately above the expected baseline.
* **HIGH** — Significant abnormal consumption requires investigation.
* **CRITICAL** — Very high deviation indicates urgent investigation is recommended.

AQUASHIELD does not assume every abnormal consumption event is a physical leak. It highlights possible causes such as leakage, overflow, unusual common-area consumption, or other operational anomalies.

---

### Water Shortage Risk

Shortage risk is evaluated using signals such as:

* Current tank fill percentage
* Water available in storage
* Estimated days of water remaining
* Current consumption level
* Incoming water supply

This enables AQUASHIELD to identify situations where consumption may be normal but available water supply is becoming critically low.

---

## Three Important Operational Scenarios

The prototype demonstrates three different types of water-management situations.

### 1. Abnormal Consumption / Potential Leak

Water consumption rises significantly above the machine-learning-predicted baseline while sufficient water remains available.

**Example:** Sunrise Enclave

Result:

```text
Leak Risk      → HIGH / CRITICAL
Shortage Risk  → LOW
```

Recommended action focuses on investigating abnormal usage or possible leakage.

---

### 2. Water Shortage

Water consumption remains relatively normal, but tank storage and estimated water availability decline rapidly.

**Example:** Royal Gardens

Result:

```text
Leak Risk      → LOW
Shortage Risk  → HIGH / CRITICAL
```

Recommended action focuses on supply replenishment, storage monitoring, and immediate conservation.

---

### 3. Leak + Shortage

Abnormal consumption occurs while available water storage is also declining.

**Example:** Urban Nest

Result:

```text
Leak Risk      → HIGH / CRITICAL
Shortage Risk  → HIGH / CRITICAL
```

This represents a particularly important operational situation because abnormal consumption can accelerate an already developing water shortage.

AQUASHIELD recommends both investigating the abnormal consumption and taking immediate water-supply and conservation measures.

---

## Dashboard Experience

The Streamlit dashboard provides five main areas:

### Overview

Provides an immediate view of:

* Leak Risk
* Shortage Risk
* Tank Level
* Estimated Water Remaining
* Actual Consumption
* Expected Consumption
* Consumption Variance
* Water Available
* Gemini Recommended Action

### Leak Analysis

Explains why leak risk was generated and compares:

**Actual Consumption vs Predicted Consumption**

over time.

### Shortage Analysis

Provides detailed visibility into:

* Tank fill percentage
* Water availability
* Estimated days remaining
* Recent tank-level trends

### Consumption Forecast

Displays historical actual consumption against the BigQuery ML expected-consumption baseline.

### AI Insights

Uses Gemini to translate quantitative water-risk signals into concise, contextual recommendations for facility managers.

---

## Solution Architecture

AQUASHIELD follows a cloud-native analytics and AI architecture:

```text
Water Consumption Data
        +
Water Supply Data
        +
Tank Level Data
        +
Apartment Profile
        +
Weather Data
        ↓
Google BigQuery
        ↓
BigQuery ML
Expected Water Consumption
        ↓
AQUASHIELD Water Intelligence Layer
        ↓
Leak Risk + Shortage Risk
        ↓
Gemini
Context-Aware Recommendations
        ↓
Streamlit Dashboard
        ↓
Google Cloud Run
```

---

## Technology Stack

AQUASHIELD currently uses:

* **Python** — Application and data-processing logic
* **Streamlit** — Interactive water-intelligence dashboard
* **Google BigQuery** — Central analytics platform
* **BigQuery ML** — Water-consumption prediction model
* **Gemini on Google Cloud** — Context-aware operational recommendations
* **Google Cloud Run** — Serverless application deployment
* **Altair** — Interactive data visualizations
* **Pandas** — Data processing and transformation

---

## Machine Learning

A BigQuery ML regression model estimates expected daily water consumption using factors such as:

* Apartment
* Day of week
* Month
* Weather
* Rain probability
* Number of residential units
* Estimated residents
* Historical baseline consumption

AQUASHIELD compares the predicted consumption with actual consumption to identify abnormal usage patterns.

---

## AI-Powered Recommendations

Gemini acts as the recommendation layer of AQUASHIELD.

Instead of simply displaying risk scores, Gemini receives contextual information such as:

* Actual and expected consumption
* Consumption variance
* Leak risk
* Shortage risk
* Tank fill percentage
* Estimated water remaining
* Conservation opportunity

Gemini then produces a concise operational recommendation explaining what the facility manager should investigate or prioritize.

---

## Current Prototype Scope

The current prototype uses synthetic apartment water-management datasets designed to simulate realistic operational scenarios.

The architecture is intentionally designed so that these synthetic sources can later be replaced by real-world inputs such as:

* Smart water meters
* IoT tank-level sensors
* Municipal supply systems
* Building-management systems
* Weather APIs
* Tanker supply records

The core analytics, machine-learning, risk-detection, and recommendation layers can remain largely unchanged as real-time data sources are introduced.

---

## Vision

AQUASHIELD aims to move water management from:

**Reactive monitoring → Predictive intelligence → Proactive conservation**

By identifying abnormal water consumption early, anticipating shortages before they become emergencies, and recommending timely interventions, AQUASHIELD can help communities reduce water wastage and manage water more responsibly.

When deployed across many residential and commercial communities, even small improvements in water efficiency can translate into meaningful conservation at scale.

---

**AQUASHIELD — Predict. Prevent. Preserve Every Drop.**
