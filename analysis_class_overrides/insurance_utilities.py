from typing import Dict, List
from ar_analytics.helpers.utils import SharedFn

class InsuranceSharedFn(SharedFn):
    def __init__(self):
        super().__init__()

    def get_formatted_num(self, num: float | int | str, met_format: str, pretty_num=False, signed=False):
        return super().get_formatted_num(num, met_format, True, signed) 
    
# Monkey patch to add metric hierarchy grouping logic
def _filter_metric_hierarchy_by_groups(current_metric, metric_hierarchy, metric_hierarchy_groups) -> List[dict]:
    """Filter metric_hierarchy based on metric_hierarchy_groups"""
    if not current_metric or not metric_hierarchy_groups or not metric_hierarchy:
        return metric_hierarchy
    
    target_group = None
    for group in metric_hierarchy_groups:
        if current_metric in group:
            target_group = group
            break
    
    if not target_group:
        return metric_hierarchy
    
    # Filter metric_hierarchy to only include metrics from the target group
    filtered_hierarchy = []
    for item in metric_hierarchy:
        metric_name = item.get('metric')
        peers = item.get('peer_metrics') or []

        # keep if the metric itself is in the group OR if any peers are in the group
        if (metric_name in target_group) or any(peer in target_group for peer in peers):
            filtered_item = item.copy()
            if peers:
                filtered_item['peer_metrics'] = [peer for peer in peers if peer in target_group]
            filtered_hierarchy.append(filtered_item)
    
    return filtered_hierarchy
