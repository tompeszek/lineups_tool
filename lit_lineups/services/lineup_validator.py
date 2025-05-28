"""
Lineup validation service
"""
from typing import List, Dict
from utils.event_utils import check_time_conflict, find_event_details

class LineupValidator:
    """Service for validating event lineups"""
    
    def _check_age_requirements(self, lineup: Dict, requirements: Dict, event_name: str) -> List[str]:
        """Check age category requirements - average age must meet minimum"""
        issues = []
        
        if not lineup['athletes']:
            return issues
        
        # Extract age categories from event name
        import re
        from models.constants import AGE_CATEGORIES
        
        age_cats_in_event = re.findall(r'\b([A-K]{1,2}(?:-[A-K]{1,2})?)\b', event_name)
        
        if not age_cats_in_event:
            return issues
        
        # Find the minimum age requirement for this event
        min_required_age = None
        for cat_group in age_cats_in_event:
            if '-' in cat_group:
                # Range like "AA-B"
                start_cat = cat_group.split('-')[0]
            else:
                # Single category like "A"
                start_cat = cat_group
            
            if start_cat in AGE_CATEGORIES:
                cat_min_age = AGE_CATEGORIES[start_cat][0]
                if min_required_age is None or cat_min_age < min_required_age:
                    min_required_age = cat_min_age
        
        if min_required_age is not None:
            # Calculate average age of rowers (excluding coxswain)
            avg_age = sum(a.age for a in lineup['athletes']) / len(lineup['athletes'])
            
            if avg_age < min_required_age:
                issues.append(f"Average age {avg_age:.1f} is below minimum {min_required_age} for this category")
        
        return issues
    
    def validate_lineup(self, lineup: Dict, requirements: Dict, event_num: int, 
                       all_lineups: Dict, spacing_minutes: int, min_gap_minutes: int) -> List[str]:
        """Validate a lineup and return list of issues"""
        issues = []
        
        # Check if lineup is complete
        issues.extend(self._check_completeness(lineup, requirements))
        
        # Check gender balance for mixed events
        issues.extend(self._check_gender_balance(lineup, requirements))
        
        # Check sweep rowing balance
        issues.extend(self._check_sweep_balance(lineup, requirements))
        
        # Check age requirements
        from utils.event_utils import find_event_details
        event_name, _ = find_event_details(event_num)
        if event_name:
            issues.extend(self._check_age_requirements(lineup, requirements, event_name))
        
        # Check time conflicts
        issues.extend(self._check_time_conflicts(lineup, event_num, all_lineups, spacing_minutes, min_gap_minutes))
        
        return issues
    
    def _check_completeness(self, lineup: Dict, requirements: Dict) -> List[str]:
        """Check if lineup is complete"""
        issues = []
        
        if len(lineup['athletes']) < requirements['num_rowers']:
            issues.append(f"Need {requirements['num_rowers'] - len(lineup['athletes'])} more rowers")
        
        if requirements['has_cox'] and not lineup['coxswain']:
            issues.append("Need a coxswain")
        
        return issues
    
    def _check_gender_balance(self, lineup: Dict, requirements: Dict) -> List[str]:
        """Check gender balance for mixed events"""
        issues = []
        
        if requirements['gender_req'] == 'Mixed' and lineup['athletes']:
            male_count = sum(1 for a in lineup['athletes'] if a.gender == 'M')
            female_count = sum(1 for a in lineup['athletes'] if a.gender == 'F')
            if male_count != female_count:
                issues.append(f"Mixed event needs equal men and women (currently {male_count}M, {female_count}F)")
        
        return issues
    
    def _check_sweep_balance(self, lineup: Dict, requirements: Dict) -> List[str]:
        """Check port/starboard balance for sweep events"""
        issues = []
        
        if not requirements['is_sculling'] and len(lineup['athletes']) > 1:
            port_rowers = sum(1 for a in lineup['athletes'] if a.can_port)
            starboard_rowers = sum(1 for a in lineup['athletes'] if a.can_starboard)
            both_sides = sum(1 for a in lineup['athletes'] if a.can_port and a.can_starboard)
            
            needed_port = requirements['num_rowers'] // 2
            needed_starboard = requirements['num_rowers'] // 2
            
            if port_rowers < needed_port and (port_rowers + both_sides) < needed_port:
                issues.append("Not enough port-side rowers available")
            if starboard_rowers < needed_starboard and (starboard_rowers + both_sides) < needed_starboard:
                issues.append("Not enough starboard-side rowers available")
        
        return issues
    
    def _check_time_conflicts(self, lineup: Dict, event_num: int, all_lineups: Dict, 
                             spacing_minutes: int, min_gap_minutes: int) -> List[str]:
        """Check for time conflicts with other events"""
        issues = []
        
        if not (lineup['athletes'] or lineup['coxswain']):
            return issues
        
        all_lineup_athletes = lineup['athletes'] + ([lineup['coxswain']] if lineup['coxswain'] else [])
        
        for athlete in all_lineup_athletes:
            conflicts = []
            for other_event, other_lineup in all_lineups.items():
                if other_event != event_num:
                    other_athletes = other_lineup['athletes'] + ([other_lineup['coxswain']] if other_lineup['coxswain'] else [])
                    if athlete in other_athletes:
                        if check_time_conflict(event_num, other_event, spacing_minutes, min_gap_minutes):
                            other_event_name, _ = find_event_details(other_event)
                            if other_event_name:
                                conflicts.append(f"Event {other_event}: {other_event_name}")
            
            if conflicts:
                issues.append(f"{athlete.name} has time conflicts with: {', '.join(conflicts)}")
        
        return issues