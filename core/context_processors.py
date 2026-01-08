from .models import SiteStats

def site_stats(request):
    stats, _ = SiteStats.objects.get_or_create(pk=1, defaults={'total_views': 0})
    return {'total_views': stats.total_views}