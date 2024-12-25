from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Return the value from a dictionary using a key."""
    return dictionary.get(key)


@register.filter
def get_task_rating(user_ratings, task_name):
    """Return the rating for a specific task from the user_ratings dictionary."""
    return user_ratings.get(task_name, 0)
