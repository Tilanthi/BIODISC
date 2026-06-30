"""
Policy-Driven Orchestration for BIODISC

Implements declarative, policy-based orchestration:
- YAML/JSON policy definitions
- Explainable orchestration decisions
- User-customizable behavior
- Domain-specific rule sets
- Policy validation and testing

This makes orchestration transparent and customizable.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import time
import yaml
import json
from pathlib import Path
import re


class PolicyType(Enum):
    """Types of orchestration policies."""
    CAPABILITY_SELECTION = "capability_selection"
    COORDINATION_PATTERN = "coordination_pattern"
    RESOURCE_ALLOCATION = "resource_allocation"
    QUALITY_THRESHOLD = "quality_threshold"
    CONFLICT_RESOLUTION = "conflict_resolution"
    DOMAIN_SPECIFIC = "domain_specific"
    USER_PREFERENCE = "user_preference"


class PolicyAction(Enum):
    """Actions that policies can trigger."""
    REQUIRE = "require"           # Must use specific capability
    PREFER = "prefer"             # Prefer specific capability
    AVOID = "avoid"               # Avoid specific capability
    CHAIN = "chain"               # Chain capabilities in order
    PARALLELIZE = "parallelize"   # Execute in parallel
    SEQUENTIALIZE = "sequentialize"  # Execute sequentially
    CONDITIONAL = "conditional"   # Conditional logic


@dataclass
class PolicyCondition:
    """Condition for policy applicability."""
    field: str  # Query field to check
    operator: str  # Comparison operator: equals, contains, regex, etc.
    value: Any  # Value to compare against

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context."""
        if self.field not in context:
            return False

        context_value = context[self.field]

        if self.operator == "equals":
            return context_value == self.value
        elif self.operator == "contains":
            return self.value in str(context_value).lower()
        elif self.operator == "regex":
            return bool(re.search(self.value, str(context_value)))
        elif self.operator == "greater_than":
            return context_value > self.value
        elif self.operator == "less_than":
            return context_value < self.value
        elif self.operator == "in":
            return context_value in self.value
        else:
            return False


@dataclass
class PolicyRule:
    """A single policy rule."""
    rule_id: str
    policy_type: PolicyType
    condition: Optional[PolicyCondition]
    action: PolicyAction
    target: str  # What the action applies to
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: float = 0.5
    explanation: str = ""
    enabled: bool = True


@dataclass
class PolicySet:
    """A collection of related policies."""
    name: str
    version: str
    description: str
    domain: Optional[str] = None
    policies: List[PolicyRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyDecision:
    """A decision made by policy engine."""
    rule_id: str
    action: PolicyAction
    target: str
    parameters: Dict[str, Any]
    explanation: str
    confidence: float
    applicable_policies: List[str]


class PolicyValidator:
    """Validate policies for correctness and safety."""

    def __init__(self):
        self.validation_rules = {
            "capability_exists": self._validate_capability_exists,
            "valid_operator": self._validate_operator,
            "valid_priority": self._validate_priority,
            "has_condition_or_always": self._validate_has_condition,
            "valid_parameters": self._validate_parameters
        }

    def validate_policy(self, policy: PolicyRule) -> List[str]:
        """
        Validate a policy rule.

        Returns list of validation errors (empty if valid).
        """
        errors = []

        for rule_name, validator in self.validation_rules.items():
            error = validator(policy)
            if error:
                errors.append(error)

        return errors

    def _validate_capability_exists(self, policy: PolicyRule) -> Optional[str]:
        """Validate that target capability exists."""
        # In real system, would check against capability registry
        return None  # Placeholder

    def _validate_operator(self, policy: PolicyRule) -> Optional[str]:
        """Validate condition operator."""
        if policy.condition:
            valid_operators = ["equals", "contains", "regex", "greater_than", "less_than", "in"]
            if policy.condition.operator not in valid_operators:
                return f"Invalid operator: {policy.condition.operator}"
        return None

    def _validate_priority(self, policy: PolicyRule) -> Optional[str]:
        """Validate priority is in range."""
        if not (0.0 <= policy.priority <= 1.0):
            return f"Priority out of range: {policy.priority}"
        return None

    def _validate_has_condition(self, policy: PolicyRule) -> Optional[str]:
        """Validate policy has condition or is meant to be unconditional."""
        return None  # Unconditional policies are allowed

    def _validate_parameters(self, policy: PolicyRule) -> Optional[str]:
        """Validate action parameters."""
        required_params = {
            PolicyAction.CHAIN: ["capabilities"],
            PolicyAction.PARALLELIZE: ["capabilities"],
            PolicyAction.SEQUENTIALIZE: ["capabilities"]
        }

        if policy.action in required_params:
            for param in required_params[policy.action]:
                if param not in policy.parameters:
                    return f"Missing required parameter: {param}"

        return None

    def validate_policy_set(self, policy_set: PolicySet) -> Dict[str, List[str]]:
        """Validate all policies in a policy set."""
        errors = {}

        for policy in policy_set.policies:
            policy_errors = self.validate_policy(policy)
            if policy_errors:
                errors[policy.rule_id] = policy_errors

        return errors


class PolicyLoader:
    """Load policies from files."""

    def __init__(self):
        self.supported_formats = ["yaml", "json"]

    def load_policy_file(self, file_path: Union[str, Path]) -> PolicySet:
        """
        Load policy set from file.

        Supports YAML and JSON formats.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Policy file not found: {file_path}")

        # Read file
        with open(file_path, 'r') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif file_path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

        # Parse into PolicySet
        return self._parse_policy_set(data)

    def _parse_policy_set(self, data: Dict[str, Any]) -> PolicySet:
        """Parse policy data into PolicySet."""
        policies = []

        for policy_data in data.get("policies", []):
            # Parse condition
            condition = None
            if "condition" in policy_data:
                cond_data = policy_data["condition"]
                condition = PolicyCondition(
                    field=cond_data["field"],
                    operator=cond_data["operator"],
                    value=cond_data["value"]
                )

            # Parse policy
            policy = PolicyRule(
                rule_id=policy_data["rule_id"],
                policy_type=PolicyType(policy_data["policy_type"]),
                condition=condition,
                action=PolicyAction(policy_data["action"]),
                target=policy_data["target"],
                parameters=policy_data.get("parameters", {}),
                priority=policy_data.get("priority", 0.5),
                explanation=policy_data.get("explanation", ""),
                enabled=policy_data.get("enabled", True)
            )

            policies.append(policy)

        return PolicySet(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            domain=data.get("domain"),
            policies=policies,
            metadata=data.get("metadata", {})
        )

    def load_policy_directory(
        self,
        directory: Union[str, Path]
    ) -> List[PolicySet]:
        """Load all policy files from directory."""
        directory = Path(directory)
        policy_sets = []

        for file_path in directory.rglob("*.yaml"):
            try:
                policy_sets.append(self.load_policy_file(file_path))
            except Exception:
                continue

        for file_path in directory.rglob("*.yml"):
            try:
                policy_sets.append(self.load_policy_file(file_path))
            except Exception:
                continue

        for file_path in directory.rglob("*.json"):
            try:
                policy_sets.append(self.load_policy_file(file_path))
            except Exception:
                continue

        return policy_sets

    def save_policy_file(
        self,
        policy_set: PolicySet,
        file_path: Union[str, Path]
    ) -> None:
        """Save policy set to file."""
        file_path = Path(file_path)

        # Convert to dict
        data = {
            "name": policy_set.name,
            "version": policy_set.version,
            "description": policy_set.description,
            "domain": policy_set.domain,
            "policies": [],
            "metadata": policy_set.metadata
        }

        for policy in policy_set.policies:
            policy_data = {
                "rule_id": policy.rule_id,
                "policy_type": policy.policy_type.value,
                "action": policy.action.value,
                "target": policy.target,
                "parameters": policy.parameters,
                "priority": policy.priority,
                "explanation": policy.explanation,
                "enabled": policy.enabled
            }

            if policy.condition:
                policy_data["condition"] = {
                    "field": policy.condition.field,
                    "operator": policy.condition.operator,
                    "value": policy.condition.value
                }

            data["policies"].append(policy_data)

        # Write file
        with open(file_path, 'w') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False)
            elif file_path.suffix == '.json':
                json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")


class PolicyEngine:
    """Execute policies and make orchestration decisions."""

    def __init__(self):
        self.policy_sets: Dict[str, PolicySet] = {}
        self.validator = PolicyValidator()
        self.decision_history: List[PolicyDecision] = []

    def load_policies(self, policy_sets: List[PolicySet]) -> int:
        """Load policy sets into engine."""
        loaded = 0

        for policy_set in policy_sets:
            # Validate
            errors = self.validator.validate_policy_set(policy_set)

            if errors:
                print(f"Validation errors in {policy_set.name}: {errors}")
                continue

            # Load
            self.policy_sets[policy_set.name] = policy_set
            loaded += 1

        return loaded

    def add_policy(self, policy_set: PolicySet) -> bool:
        """Add a policy set to the engine."""
        errors = self.validator.validate_policy_set(policy_set)

        if errors:
            return False

        self.policy_sets[policy_set.name] = policy_set
        return True

    def evaluate_policies(
        self,
        context: Dict[str, Any],
        policy_type: Optional[PolicyType] = None
    ) -> List[PolicyDecision]:
        """
        Evaluate policies against context.

        Args:
            context: Orchestration context
            policy_type: Optional filter by policy type

        Returns:
            List of applicable policy decisions
        """
        decisions = []

        # Get applicable policies
        for policy_set in self.policy_sets.values():
            for policy in policy_set.policies:
                if not policy.enabled:
                    continue

                # Filter by type if specified
                if policy_type and policy.policy_type != policy_type:
                    continue

                # Check condition
                if policy.condition:
                    if not policy.condition.evaluate(context):
                        continue

                # Create decision
                decision = PolicyDecision(
                    rule_id=policy.rule_id,
                    action=policy.action,
                    target=policy.target,
                    parameters=policy.parameters,
                    explanation=policy.explanation,
                    confidence=policy.priority,
                    applicable_policies=[policy_set.name]
                )

                decisions.append(decision)

        # Sort by priority
        decisions.sort(key=lambda d: d.confidence, reverse=True)

        return decisions

    def select_capabilities(
        self,
        available: List[str],
        context: Dict[str, Any]
    ) -> PolicyDecision:
        """Select capabilities based on policies."""
        decisions = self.evaluate_policies(
            context,
            PolicyType.CAPABILITY_SELECTION
        )

        if not decisions:
            # No policies - return default decision
            return PolicyDecision(
                rule_id="default",
                action=PolicyAction.PREFER,
                target="all",
                parameters={"capabilities": available},
                explanation="No applicable policies - using all available capabilities",
                confidence=0.0,
                applicable_policies=[]
            )

        # Use highest priority decision
        return decisions[0]

    def select_coordination_pattern(
        self,
        available_patterns: List[str],
        context: Dict[str, Any]
    ) -> PolicyDecision:
        """Select coordination pattern based on policies."""
        decisions = self.evaluate_policies(
            context,
            PolicyType.COORDINATION_PATTERN
        )

        if not decisions:
            # No policies - return default
            return PolicyDecision(
                rule_id="default",
                action=PolicyAction.PREFER,
                target="centralized",
                parameters={},
                explanation="No applicable policies - using centralized pattern",
                confidence=0.0,
                applicable_policies=[]
            )

        return decisions[0]

    def resolve_conflicts(
        self,
        conflicting_decisions: List[PolicyDecision],
        context: Dict[str, Any]
    ) -> List[PolicyDecision]:
        """Resolve conflicts between policy decisions."""
        # Sort by priority
        conflicting_decisions.sort(key=lambda d: d.confidence, reverse=True)

        # Check for action conflicts
        action_groups = {}
        for decision in conflicting_decisions:
            if decision.action not in action_groups:
                action_groups[decision.action] = []
            action_groups[decision.action].append(decision)

        # For each action type, keep highest priority
        resolved = []
        for action, decisions in action_groups.items():
            resolved.append(decisions[0])  # Highest priority

        return resolved

    def explain_decision(self, decision: PolicyDecision) -> str:
        """Generate explanation for a policy decision."""
        explanation = f"Decision: {decision.action.value} {decision.target}"

        if decision.explanation:
            explanation += f"\nReason: {decision.explanation}"

        if decision.applicable_policies:
            explanation += f"\nPolicies: {', '.join(decision.applicable_policies)}"

        return explanation

    def get_policy_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded policies."""
        total_policies = sum(
            len(ps.policies) for ps in self.policy_sets.values()
        )

        enabled_policies = sum(
            sum(1 for p in ps.policies if p.enabled)
            for ps in self.policy_sets.values()
        )

        policy_type_counts = defaultdict(int)
        for policy_set in self.policy_sets.values():
            for policy in policy_set.policies:
                policy_type_counts[policy.policy_type.value] += 1

        return {
            "policy_sets": len(self.policy_sets),
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "policy_type_distribution": dict(policy_type_counts),
            "decisions_made": len(self.decision_history)
        }


class PolicyDrivenOrchestrator:
    """
    Main policy-driven orchestrator.

    Uses policies to drive all orchestration decisions:
    - Capability selection
    - Coordination patterns
    - Resource allocation
    - Quality thresholds
    """

    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.policy_loader = PolicyLoader()

    def load_policies_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load policies from file."""
        try:
            policy_set = self.policy_loader.load_policy_file(file_path)
            return self.policy_engine.add_policy(policy_set)
        except Exception:
            return False

    def load_policies_from_directory(self, directory: Union[str, Path]) -> int:
        """Load all policies from directory."""
        policy_sets = self.policy_loader.load_policy_directory(directory)
        return self.policy_engine.load_policies(policy_sets)

    def orchestrate_with_policies(
        self,
        query: str,
        available_capabilities: List[str],
        available_patterns: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate using policies.

        Args:
            query: User query
            available_capabilities: Available capabilities
            available_patterns: Available coordination patterns
            context: Orchestration context

        Returns:
            Orchestration plan with policy decisions
        """
        if context is None:
            context = {}

        # Add query to context
        context["query"] = query
        context["available_capabilities"] = available_capabilities

        # Get policy-driven decisions
        capability_decision = self.policy_engine.select_capabilities(
            available_capabilities,
            context
        )

        pattern_decision = self.policy_engine.select_coordination_pattern(
            available_patterns,
            context
        )

        # Apply decisions
        selected_capabilities = self._apply_capability_decision(
            capability_decision,
            available_capabilities
        )

        selected_pattern = self._apply_pattern_decision(
            pattern_decision,
            available_patterns
        )

        # Record decisions
        self.policy_engine.decision_history.append(capability_decision)
        self.policy_engine.decision_history.append(pattern_decision)

        return {
            "selected_capabilities": selected_capabilities,
            "coordination_pattern": selected_pattern,
            "capability_decision": capability_decision,
            "pattern_decision": pattern_decision,
            "explanations": {
                "capabilities": self.policy_engine.explain_decision(capability_decision),
                "pattern": self.policy_engine.explain_decision(pattern_decision)
            },
            "policy_compliance": True
        }

    def _apply_capability_decision(
        self,
        decision: PolicyDecision,
        available: List[str]
    ) -> List[str]:
        """Apply capability selection decision."""
        if decision.action == PolicyAction.REQUIRE:
            if decision.target in available:
                return [decision.target]
            else:
                return []

        elif decision.action == PolicyAction.PREFER:
            if decision.target == "all":
                return available
            elif decision.target in available:
                # Put preferred first
                result = [decision.target]
                result.extend(c for c in available if c != decision.target)
                return result

        elif decision.action == PolicyAction.AVOID:
            return [c for c in available if c != decision.target]

        elif decision.action == PolicyAction.CHAIN:
            chain = decision.parameters.get("capabilities", [])
            return [c for c in chain if c in available]

        elif decision.action == PolicyAction.PARALLELIZE:
            return decision.parameters.get("capabilities", available)

        # Default
        return available

    def _apply_pattern_decision(
        self,
        decision: PolicyDecision,
        available: List[str]
    ) -> str:
        """Apply coordination pattern decision."""
        if decision.action == PolicyAction.REQUIRE:
            if decision.target in available:
                return decision.target

        elif decision.action == PolicyAction.PREFER:
            if decision.target in available:
                return decision.target

        # Default
        return available[0] if available else "centralized"

    def create_policy(
        self,
        rule_id: str,
        policy_type: PolicyType,
        condition: Optional[Dict[str, Any]],
        action: PolicyAction,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: float = 0.5,
        explanation: str = ""
    ) -> PolicyRule:
        """Create a new policy rule."""
        # Parse condition
        cond = None
        if condition:
            cond = PolicyCondition(
                field=condition["field"],
                operator=condition["operator"],
                value=condition["value"]
            )

        return PolicyRule(
            rule_id=rule_id,
            policy_type=policy_type,
            condition=cond,
            action=action,
            target=target,
            parameters=parameters or {},
            priority=priority,
            explanation=explanation
        )

    def save_policy(self, policy_set: PolicySet, file_path: Union[str, Path]) -> None:
        """Save policy set to file."""
        self.policy_loader.save_policy_file(policy_set, file_path)

    def get_policy_report(self) -> Dict[str, Any]:
        """Get comprehensive policy report."""
        stats = self.policy_engine.get_policy_statistics()

        return {
            "statistics": stats,
            "recent_decisions": [
                {
                    "action": d.action.value,
                    "target": d.target,
                    "confidence": d.confidence,
                    "explanation": d.explanation
                }
                for d in self.policy_engine.decision_history[-10:]
            ],
            "policy_sets": list(self.policy_engine.keys())
        }


def create_policy_driven_orchestrator() -> PolicyDrivenOrchestrator:
    """Factory function to create policy-driven orchestrator."""
    return PolicyDrivenOrchestrator()


from collections import defaultdict
