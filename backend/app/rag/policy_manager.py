import json
import os
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PolicyManager:
    def __init__(self, policies_dir: str = "./policies"):
        """Initialize policy manager with policies directory"""
        self.policies_dir = policies_dir
        self.policies = {}
        self.load_policies()
    
    def load_policies(self):
        """Load all policy files from the policies directory"""
        try:
            if not os.path.exists(self.policies_dir):
                logger.warning(f"Policies directory {self.policies_dir} does not exist")
                return
            
            for filename in os.listdir(self.policies_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.policies_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        policy_name = filename.replace('.json', '')
                        self.policies[policy_name] = json.load(f)
                        logger.info(f"✅ Loaded policy: {policy_name}")
            
            logger.info(f"✅ Loaded {len(self.policies)} policy files")
            
        except Exception as e:
            logger.error(f"❌ Error loading policies: {e}")
            raise
    
    def get_policies(self, domain: str = None) -> Dict[str, Any]:
        """Get policies for a specific domain or all policies"""
        if domain:
            return self.policies.get(domain, {})
        return self.policies
    
    def get_leave_policies(self) -> Dict[str, Any]:
        """Get leave-related policies"""
        return self.policies.get('leave_policies', {})
    
    def get_attendance_policies(self) -> Dict[str, Any]:
        """Get attendance-related policies"""
        return self.policies.get('attendance_policies', {})
    
    def get_event_policies(self) -> Dict[str, Any]:
        """Get event-related policies"""
        return self.policies.get('event_policies', {})
    
    def validate_leave_request(self, leave_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate leave request against policies"""
        try:
            leave_policies = self.get_leave_policies()
            leave_types = leave_policies.get('leave_types', {})
            
            leave_type = leave_data.get('leave_type')
            if leave_type not in leave_types:
                return {
                    'valid': False,
                    'error': f'Invalid leave type: {leave_type}',
                    'allowed_types': list(leave_types.keys())
                }
            
            policy = leave_types[leave_type]
            start_date = datetime.fromisoformat(leave_data['start_date'])
            end_date = datetime.fromisoformat(leave_data['end_date'])
            
            # Calculate leave duration
            duration = (end_date - start_date).days + 1
            
            # Check maximum days allowed
            max_days = policy.get('max_days_per_semester', 30)
            if duration > max_days:
                return {
                    'valid': False,
                    'error': f'Leave duration ({duration} days) exceeds maximum allowed ({max_days} days)',
                    'max_allowed': max_days
                }
            
            # Check advance notice requirement
            if policy.get('advance_notice_required', False):
                min_advance_days = policy.get('min_advance_days', 3)
                days_until_start = (start_date - datetime.now()).days
                if days_until_start < min_advance_days:
                    return {
                        'valid': False,
                        'error': f'Advance notice of {min_advance_days} days required',
                        'days_until_start': days_until_start
                    }
            
            # Check auto-approve threshold
            auto_approve_threshold = policy.get('auto_approve_threshold', 0)
            auto_approve = duration <= auto_approve_threshold
            
            return {
                'valid': True,
                'auto_approve': auto_approve,
                'requires_certificate': policy.get('requires_certificate', False),
                'max_days': max_days,
                'duration': duration
            }
            
        except Exception as e:
            logger.error(f"❌ Error validating leave request: {e}")
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def validate_attendance_requirements(self, attendance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate attendance against minimum requirements"""
        try:
            attendance_policies = self.get_attendance_policies()
            minimum_requirements = attendance_policies.get('minimum_requirements', {})
            
            attendance_percentage = attendance_data.get('attendance_percentage', 0)
            session_type = attendance_data.get('session_type', 'lecture')
            
            # Get minimum requirement for session type
            min_requirement = minimum_requirements.get(f'{session_type}_attendance', 75)
            
            # Check if attendance meets minimum requirement
            meets_requirement = attendance_percentage >= min_requirement
            
            # Get warning thresholds
            warning_thresholds = attendance_policies.get('warning_thresholds', {})
            first_warning = warning_thresholds.get('first_warning', 70)
            second_warning = warning_thresholds.get('second_warning', 65)
            final_warning = warning_thresholds.get('final_warning', 60)
            
            warning_level = None
            if attendance_percentage < final_warning:
                warning_level = 'final'
            elif attendance_percentage < second_warning:
                warning_level = 'second'
            elif attendance_percentage < first_warning:
                warning_level = 'first'
            
            return {
                'meets_requirement': meets_requirement,
                'attendance_percentage': attendance_percentage,
                'minimum_required': min_requirement,
                'warning_level': warning_level,
                'session_type': session_type
            }
            
        except Exception as e:
            logger.error(f"❌ Error validating attendance: {e}")
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def validate_event_registration(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event registration against policies"""
        try:
            event_policies = self.get_event_policies()
            registration_rules = event_policies.get('registration_rules', {})
            
            # Check advance booking requirement
            advance_booking_days = registration_rules.get('advance_booking_days', 7)
            event_date = datetime.fromisoformat(event_data['start_datetime'])
            days_until_event = (event_date - datetime.now()).days
            
            if days_until_event < advance_booking_days:
                return {
                    'valid': False,
                    'error': f'Event registration requires {advance_booking_days} days advance booking',
                    'days_until_event': days_until_event
                }
            
            # Check cancellation deadline
            cancellation_deadline_hours = registration_rules.get('cancellation_deadline_hours', 24)
            
            return {
                'valid': True,
                'advance_booking_days': advance_booking_days,
                'cancellation_deadline_hours': cancellation_deadline_hours,
                'days_until_event': days_until_event
            }
            
        except Exception as e:
            logger.error(f"❌ Error validating event registration: {e}")
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    def get_policy_summary(self, domain: str) -> Dict[str, Any]:
        """Get a summary of policies for a specific domain"""
        policies = self.get_policies(domain)
        if not policies:
            return {'error': f'No policies found for domain: {domain}'}
        
        summary = {
            'domain': domain,
            'last_updated': datetime.now().isoformat(),
            'policy_count': len(policies),
            'key_rules': []
        }
        
        if domain == 'leave_policies':
            leave_types = policies.get('leave_types', {})
            summary['key_rules'] = [
                f"{lt}: max {details.get('max_days_per_semester', 'N/A')} days"
                for lt, details in leave_types.items()
            ]
        elif domain == 'attendance_policies':
            min_req = policies.get('minimum_requirements', {})
            summary['key_rules'] = [
                f"{req_type}: {req_value}% minimum"
                for req_type, req_value in min_req.items()
            ]
        elif domain == 'event_policies':
            reg_rules = policies.get('registration_rules', {})
            summary['key_rules'] = [
                f"Advance booking: {reg_rules.get('advance_booking_days', 'N/A')} days",
                f"Cancellation deadline: {reg_rules.get('cancellation_deadline_hours', 'N/A')} hours"
            ]
        
        return summary
    
    def update_policy(self, domain: str, policy_data: Dict[str, Any]) -> bool:
        """Update a policy file"""
        try:
            file_path = os.path.join(self.policies_dir, f"{domain}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(policy_data, f, indent=2, ensure_ascii=False)
            
            # Reload the policy
            self.policies[domain] = policy_data
            logger.info(f"✅ Updated policy: {domain}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating policy {domain}: {e}")
            return False
    
    def get_all_policy_summaries(self) -> Dict[str, Any]:
        """Get summaries for all policies"""
        summaries = {}
        for domain in self.policies.keys():
            summaries[domain] = self.get_policy_summary(domain)
        return summaries
