import datetime

class PlantHealthTracker:
    """
    Core logic for tracking plant growth stages and health history.
    """
    def __init__(self, plant_id):
        self.plant_id = plant_id
        self.logs = []

    def add_log(self, health_score, status_note):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "health_score": health_score,
            "status": status_note
        }
        self.logs.append(log_entry)
        return log_entry

class CareReminders:
    """
    Logic for generating smart care notifications based on plant needs.
    """
    @staticmethod
    def get_watering_reminder(species_name, last_watered_days):
        # Placeholder for species-specific logic
        return f"🌿 Reminder: Your {species_name} needs water today."
