# AQUASHIELD

AQUASHIELD is an AI-powered water management prototype designed to help apartment communities monitor water consumption, detect abnormal usage, identify shortage risks, and recommend conservation actions.

The prototype combines:

- BigQuery for data storage and analytics
- Python for data processing and application logic
- Streamlit for the web dashboard
- Google Cloud Run for deployment
- Looker Studio for analytics visualization

## Key Features

### 1. Apartment-Level Monitoring
Users can select an apartment and view its water-management metrics.

### 2. Historical Date Selection
Users can select a specific historical date to inspect the system state and model output for that day.

### 3. Actual vs Predicted Consumption
AQUASHIELD compares actual water usage with predicted consumption to identify abnormal consumption patterns.

### 4. Leak Risk Detection
The prototype identifies persistent excess consumption and classifies leak risk as:

- LOW
- MEDIUM
- HIGH

### 5. Water Shortage Risk
AQUASHIELD evaluates available water, tank levels, and estimated remaining supply to classify shortage risk.

### 6. Tank Monitoring
The dashboard displays:

- Tank fill percentage
- Available water
- Estimated days of water remaining

### 7. Conservation Opportunity
The system estimates how much water could potentially be conserved when actual consumption exceeds expected usage.

### 8. Recommended Actions
Based on detected conditions, AQUASHIELD provides operational recommendations such as:

- Investigating possible leaks
- Reviewing abnormal water usage
- Reducing non-essential consumption
- Reviewing water supply when shortage risk is high

## Example Test Scenarios

### High Leak Risk / Low Shortage Risk

Apartment: Palm Meadows  
Date: 2026-05-30

Expected behaviour:

- Leak Risk: HIGH
- Shortage Risk: LOW
- Tank Fill: approximately 61.88%
- Estimated Days Remaining: approximately 0.74 days

This demonstrates abnormal water consumption while sufficient water is still available.

### Low Leak Risk / High Shortage Risk

Apartment: Eco Homes  
Date: 2026-04-11

Expected behaviour:

- Leak Risk: LOW
- Shortage Risk: HIGH
- Tank Fill: approximately 35.67%
- Estimated Days Remaining: approximately 0.47 days

This demonstrates a water-shortage condition without abnormal consumption.


## Architecture

```text
Water Consumption / Supply / Tank Data
                |
                v
          Google BigQuery
                |
                v
      AQUASHIELD Analytics Logic
                |
        +-------+-------+
        |               |
        v               v
   Streamlit         Looker Studio
        |
        v
 Google Cloud Run
        |
        v
  AQUASHIELD Web App