from django.test import SimpleTestCase
from django.urls import reverse


class ProductPagesTestCase(SimpleTestCase):
    """Every product page must render without errors."""

    def test_meal_planner(self):
        response = self.client.get(reverse('web:meal_planner'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Meal Planner')

    def test_daily_summary(self):
        response = self.client.get(reverse('web:daily_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daily Summary')

    def test_water_tracker(self):
        response = self.client.get(reverse('web:water_tracker'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Water')

    def test_food_admin(self):
        response = self.client.get(reverse('web:food_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Food Management')

    def test_static_asset_references_are_valid(self):
        """The templates must reference static files, not missing local files."""
        for view in ['meal_planner', 'daily_summary', 'water_tracker', 'food_admin']:
            response = self.client.get(reverse(f'web:{view}'))
            self.assertNotContains(
                response, 'src="script.js"',
                msg_prefix=f'{view} references an unmigrated asset',
                status_code=response.status_code,
            )