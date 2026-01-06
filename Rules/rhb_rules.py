def evaluate_rhb_parameter_1(experian_data):
    """
    RHB Parameter 1: No Legal Suits at All
    """
    if experian_data["legal_suits_count"] == 0:
        return {
            "status": "Pass",
            "detail": "No legal suits detected in Experian report"
        }

    return {
        "status": "Fail",
        "detail": f"{experian_data['legal_suits_count']} legal suit(s) detected in Experian report"
    }
