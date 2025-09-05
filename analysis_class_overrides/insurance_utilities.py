from typing import Dict
from ar_analytics.helpers.utils import SharedFn

class InsuranceSharedFn(SharedFn):
    def __init__(self):
        super().__init__()

    def get_formatted_num(self, num: float | int | str, met_format: str, pretty_num=False, signed=False):
        return super().get_formatted_num(num, met_format, True, signed) 
    
# Monkey patch to add metric hierarchy grouping logic
def _filter_metric_hierarchy_by_groups(current_metric, metric_hierarchy, metric_hierarchy_groups) -> list:
    """Filter metric_hierarchy based on metric_hierarchy_groups"""
    if not current_metric:
        return
    
    if not metric_hierarchy_groups or not metric_hierarchy:
        return
    
    target_group = None
    for group in metric_hierarchy_groups:
        if current_metric in group:
            target_group = group
            break
    
    if not target_group:
        return
    
    # Filter metric_hierarchy to only include metrics from the target group
    filtered_hierarchy = []
    for item in metric_hierarchy:
        metric_name = item.get('metric')
        if metric_name in target_group:
            filtered_item = item.copy()
            if 'peer_metrics' in filtered_item and filtered_item['peer_metrics']:
                filtered_peers = [peer for peer in filtered_item['peer_metrics'] if peer in target_group]
                filtered_item['peer_metrics'] = filtered_peers
            filtered_hierarchy.append(filtered_item)
    
    return filtered_hierarchy
