"""
Cost Matrix Optimization Engine.
Calculates exception-handling financial loss ($) rather than relying only on F1 score.
Reflects asymmetric cost structure: Missed Duplicate ($94,000 loss) vs Unnecessary Escalation ($15 cost).
"""

from typing import Dict, Any, List

class FinancialCostOptimizer:
    def __init__(self, missed_duplicate_cost: float = 94000.0, unnecessary_escalation_cost: float = 15.0, wrong_resolution_cost: float = 50.0):
        self.MISSED_DUPLICATE_COST = missed_duplicate_cost
        self.UNNECESSARY_ESCALATION_COST = unnecessary_escalation_cost
        self.WRONG_RESOLUTION_COST = wrong_resolution_cost

    def calculate_total_financial_loss(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates total dollar loss across a dataset based on prediction decisions vs ground truth.
        """
        missed_duplicates = 0
        unnecessary_escalations = 0
        wrong_resolutions = 0
        correct_auto_actions = 0

        for pred in predictions:
            ground_truth = pred.get("ground_truth_defect")
            assigned_cat = pred.get("classification_category")
            expected_category = {
                "PERFECT_MATCH": "CLEARED_AUTO_MATCH",
                "TRUE_DUPLICATE": "TRUE_DUPLICATE_RISK",
                "QUANTITY_MISMATCH": "QUANTITY_MISMATCH",
                "PRICE_DRIFT": "PRICE_DRIFT",
                "TAX_DISCREPANCY": "TAX_DISCREPANCY",
                "MISSING_GOODS_RECEIPT": "MISSING_GOODS_RECEIPT",
                "SUBSCRIPTION_TRAP": "VALID_SUBSCRIPTION_RECURRING",
                "EXTRACTION_NOISE_UNSURE": "UNSURE_NEEDS_HUMAN_CHECK"
            }.get(ground_truth, ground_truth)

            # 1. Missed Duplicate Check (Catastrophic Error)
            if ground_truth == "TRUE_DUPLICATE" and assigned_cat != "TRUE_DUPLICATE_RISK":
                missed_duplicates += 1

            # 2. Unnecessary Human Escalation Check (Minor Error)
            elif ground_truth in ["PERFECT_MATCH", "VALID_SUBSCRIPTION_RECURRING"] and assigned_cat == "UNSURE_NEEDS_HUMAN_CHECK":
                unnecessary_escalations += 1

            # 3. Wrong Resolution Classification
            elif ground_truth != "TRUE_DUPLICATE" and assigned_cat != expected_category and assigned_cat != "UNSURE_NEEDS_HUMAN_CHECK":
                wrong_resolutions += 1

            else:
                correct_auto_actions += 1

        total_dup_loss = missed_duplicates * self.MISSED_DUPLICATE_COST
        total_escalation_loss = unnecessary_escalations * self.UNNECESSARY_ESCALATION_COST
        total_wrong_res_loss = wrong_resolutions * self.WRONG_RESOLUTION_COST

        total_financial_loss = total_dup_loss + total_escalation_loss + total_wrong_res_loss

        return {
            "total_financial_loss_dollars": total_financial_loss,
            "cost_breakdown": {
                "missed_duplicates_count": missed_duplicates,
                "missed_duplicates_loss_dollars": total_dup_loss,
                "unnecessary_escalations_count": unnecessary_escalations,
                "unnecessary_escalation_loss_dollars": total_escalation_loss,
                "wrong_resolutions_count": wrong_resolutions,
                "wrong_resolution_loss_dollars": total_wrong_res_loss,
                "correct_auto_actions_count": correct_auto_actions
            },
            "cost_matrix_parameters": {
                "missed_duplicate_cost": self.MISSED_DUPLICATE_COST,
                "unnecessary_escalation_cost": self.UNNECESSARY_ESCALATION_COST,
                "wrong_resolution_cost": self.WRONG_RESOLUTION_COST
            }
        }
