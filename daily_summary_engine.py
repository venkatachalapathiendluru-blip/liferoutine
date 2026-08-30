from datetime import datetime, date
from typing import Dict, List, Tuple, Any
import json


class DailySummaryEngine:
    """
    Daily summary engine for LifeRoutine360 application.
    Calculates and summarizes daily performance across tasks, water intake, and calories.
    """
    
    def __init__(self):
        self.water_targets = {
            'default': 3000,  # ml per day
            'high_activity': 3500,
            'low_activity': 2500
        }
        
        self.calorie_targets = {
            'weight_loss': {'min': 1500, 'max': 1800},
            'weight_gain': {'min': 2500, 'max': 3000},
            'maintenance': {'min': 1800, 'max': 2200}
        }
    
    def calculate_daily_summary(self, 
                             planned_tasks: List[Dict[str, Any]], 
                             completed_tasks: List[Dict[str, Any]], 
                             water_consumed: int, 
                             water_target: int = None,
                             calories_consumed: int = 0,
                             calorie_target_min: int = None,
                             calorie_target_max: int = None) -> Dict[str, Any]:
        """
        Calculate comprehensive daily summary.
        
        Args:
            planned_tasks: List of planned tasks/activities
            completed_tasks: List of completed tasks/activities
            water_consumed: Total water consumed in ml
            water_target: Target water consumption in ml (optional)
            calories_consumed: Total calories consumed
            calorie_target_min: Minimum target calories (optional)
            calorie_target_max: Maximum target calories (optional)
            
        Returns:
            Dictionary containing summary data
        """
        
        # Use defaults if targets not provided
        if water_target is None:
            water_target = self.water_targets['default']
            
        if calorie_target_min is None:
            calorie_target_min = self.calorie_targets['maintenance']['min']
        if calorie_target_max is None:
            calorie_target_max = self.calorie_targets['maintenance']['max']
        
        # Calculate task completion metrics
        task_completion = self._calculate_task_completion(planned_tasks, completed_tasks)
        
        # Calculate water metrics
        water_metrics = self._calculate_water_metrics(water_consumed, water_target)
        
        # Calculate calorie metrics
        calorie_metrics = self._calculate_calorie_metrics(calories_consumed, calorie_target_min, calorie_target_max)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(task_completion, water_metrics, calorie_metrics)
        
        # Generate summary message
        summary_message = self._generate_summary_message(overall_score, task_completion, water_metrics, calorie_metrics)
        
        return {
            'date': date.today().isoformat(),
            'overall_score': overall_score,
            'summary_message': summary_message,
            'tasks': task_completion,
            'water': water_metrics,
            'calories': calorie_metrics,
            'recommendations': self._generate_recommendations(task_completion, water_metrics, calorie_metrics)
        }
    
    def _calculate_task_completion(self, planned: List[Dict], completed: List[Dict]) -> Dict[str, Any]:
        """Calculate task completion metrics."""
        planned_count = len(planned)
        completed_count = len(completed)
        
        completion_rate = (completed_count / planned_count * 100) if planned_count > 0 else 0
        
        return {
            'planned': planned_count,
            'completed': completed_count,
            'completion_rate': completion_rate,
            'score': self._get_completion_score(completion_rate)
        }
    
    def _calculate_water_metrics(self, consumed: int, target: int) -> Dict[str, Any]:
        """Calculate water intake metrics."""
        consumption_rate = (consumed / target * 100) if target > 0 else 0
        remaining = max(0, target - consumed)
        
        return {
            'consumed': consumed,
            'target': target,
            'remaining': remaining,
            'consumption_rate': consumption_rate,
            'score': self._get_water_score(consumption_rate)
        }
    
    def _calculate_calorie_metrics(self, consumed: int, target_min: int, target_max: int) -> Dict[str, Any]:
        """Calculate calorie intake metrics."""
        # Determine if within target range
        if target_min <= consumed <= target_max:
            target_status = 'excellent'
            adherence_score = 100
        elif consumed < target_min:
            target_status = 'low'
            # Calculate how close to minimum
            adherence_score = max(0, (consumed / target_min) * 80)
        else:
            target_status = 'high'
            # Calculate how close to maximum
            adherence_score = max(0, 100 - ((consumed - target_max) / target_max * 50))
        
        return {
            'consumed': consumed,
            'target_min': target_min,
            'target_max': target_max,
            'target_range': f"{target_min}-{target_max}",
            'target_status': target_status,
            'adherence_score': adherence_score,
            'score': self._get_calorie_score(target_status, adherence_score)
        }
    
    def _calculate_overall_score(self, tasks: Dict, water: Dict, calories: Dict) -> Dict[str, Any]:
        """Calculate overall performance score."""
        task_weight = 0.4
        water_weight = 0.3
        calorie_weight = 0.3
        
        overall_score = (
            tasks['score'] * task_weight +
            water['score'] * water_weight +
            calories['score'] * calorie_weight
        )
        
        # Determine performance category
        if overall_score >= 90:
            category = 'Excellent'
            color = '#27ae60'
            icon = '🌟'
        elif overall_score >= 75:
            category = 'Good'
            color = '#2ecc71'
            icon = '👏'
        elif overall_score >= 60:
            category = 'Improve'
            color = '#f39c12'
            icon = '📈'
        else:
            category = 'Needs Attention'
            color = '#e74c3c'
            icon = '🎯'
        
        return {
            'score': round(overall_score, 1),
            'category': category,
            'color': color,
            'icon': icon
        }
    
    def _generate_summary_message(self, overall: Dict, tasks: Dict, water: Dict, calories: Dict) -> str:
        """Generate a simple summary message."""
        category = overall['category']
        icon = overall['icon']
        
        base_messages = {
            'Excellent': [
                f"{icon} Outstanding day! You've crushed your goals across all areas.",
                f"{icon} Perfect execution! Your consistency is paying off beautifully.",
                f"{icon} Exceptional performance! You're at the top of your game."
            ],
            'Good': [
                f"{icon} Great job! You're doing well and making solid progress.",
                f"{icon} Well done! Your efforts are really showing results.",
                f"{icon} Nice work! Keep up this positive momentum."
            ],
            'Improve': [
                f"{icon} Good effort! A few adjustments will make a big difference.",
                f"{icon} Decent progress! Focus on consistency for better results.",
                f"{icon} Keep trying! Small improvements will lead to success."
            ],
            'Needs Attention': [
                f"{icon} Room for improvement! Let's focus on building better habits.",
                f"{icon} Let's refocus! Small steps forward will help you reach your goals.",
                f"{icon} Time for change! Every day is a new opportunity to improve."
            ]
        }
        
        import random
        message = random.choice(base_messages[category])
        
        # Add specific insights
        insights = []
        
        if tasks['completion_rate'] < 80:
            insights.append(f"Task completion was {tasks['completion_rate']:.0f}%")
        
        if water['consumption_rate'] < 80:
            insights.append(f"Water intake was {water['consumption_rate']:.0f}% of target")
        
        if calories['target_status'] != 'excellent':
            insights.append(f"Calories were {calories['target_status']}")
        
        if insights:
            message += f" ({', '.join(insights)})."
        else:
            message += " You're on track for optimal health!"
        
        return message
    
    def _get_completion_score(self, rate: float) -> float:
        """Convert completion rate to score (0-100)."""
        return min(100, rate)
    
    def _get_water_score(self, rate: float) -> float:
        """Convert water consumption rate to score (0-100)."""
        if rate >= 100:
            return 100
        elif rate >= 80:
            return 90
        elif rate >= 60:
            return 75
        elif rate >= 40:
            return 50
        else:
            return max(0, rate * 0.8)
    
    def _get_calorie_score(self, status: str, adherence: float) -> float:
        """Convert calorie status to score (0-100)."""
        if status == 'excellent':
            return 100
        elif status == 'low':
            return adherence * 0.8
        elif status == 'high':
            return adherence
        else:
            return 50
    
    def _generate_recommendations(self, tasks: Dict, water: Dict, calories: Dict) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Task recommendations
        if tasks['completion_rate'] < 60:
            recommendations.append("Focus on completing more planned tasks tomorrow")
        elif tasks['completion_rate'] < 80:
            recommendations.append("Try to increase task completion consistency")
        
        # Water recommendations
        if water['consumption_rate'] < 50:
            recommendations.append("Set hourly water reminders to stay hydrated")
        elif water['consumption_rate'] < 80:
            recommendations.append("Increase water intake gradually throughout the day")
        
        # Calorie recommendations
        if calories['target_status'] == 'low':
            recommendations.append("Add nutrient-dense snacks to reach your calorie goals")
        elif calories['target_status'] == 'high':
            recommendations.append("Focus on portion control and lighter meal options")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Maintain this excellent performance!")
        
        return recommendations
    
    def export_summary(self, summary_data: Dict[str, Any]) -> str:
        """Export summary as JSON string."""
        return json.dumps(summary_data, indent=2, default=str)
    
    def get_weekly_trend(self, daily_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze weekly trends from daily summaries."""
        if len(daily_summaries) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        scores = [day['overall_score']['score'] for day in daily_summaries]
        avg_score = sum(scores) / len(scores)
        
        # Calculate trend
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / min(3, len(scores))
            earlier_avg = sum(scores[:-3]) / max(1, len(scores) - 3) if len(scores) > 3 else scores[0]
            trend = recent_avg - earlier_avg
        else:
            trend = 0
        
        trend_direction = 'improving' if trend > 5 else 'declining' if trend < -5 else 'stable'
        
        return {
            'average_score': round(avg_score, 1),
            'trend': trend_direction,
            'trend_value': round(trend, 1),
            'best_day': max(daily_summaries, key=lambda x: x['overall_score']['score'])['date'],
            'worst_day': min(daily_summaries, key=lambda x: x['overall_score']['score'])['date']
        }


# Example usage
if __name__ == "__main__":
    engine = DailySummaryEngine()
    
    # Example data
    planned_tasks = [
        {'id': 1, 'name': 'Morning Walk', 'time': '06:30'},
        {'id': 2, 'name': 'Breakfast', 'time': '08:00'},
        {'id': 3, 'name': 'Lunch', 'time': '13:00'},
        {'id': 4, 'name': 'Water Intake - AM', 'time': '10:00'},
        {'id': 5, 'name': 'Water Intake - PM', 'time': '15:00'}
    ]
    
    completed_tasks = [
        {'id': 1, 'name': 'Morning Walk', 'time': '06:30'},
        {'id': 2, 'name': 'Breakfast', 'time': '08:00'},
        {'id': 4, 'name': 'Water Intake - AM', 'time': '10:00'}
    ]
    
    summary = engine.calculate_daily_summary(
        planned_tasks=planned_tasks,
        completed_tasks=completed_tasks,
        water_consumed=2200,
        water_target=3000,
        calories_consumed=1850,
        calorie_target_min=1800,
        calorie_target_max=2200
    )
    
    print("Daily Summary Generated:")
    print("=" * 50)
    print(f"Overall Score: {summary['overall_score']['score']}% ({summary['overall_score']['category']})")
    print(f"Message: {summary['summary_message']}")
    print(f"\nTask Completion: {summary['tasks']['completion_rate']:.1f}%")
    print(f"Water Intake: {summary['water']['consumption_rate']:.1f}%")
    print(f"Calorie Target: {summary['calories']['target_status']}")
    print(f"\nRecommendations:")
    for rec in summary['recommendations']:
        print(f"  - {rec}")