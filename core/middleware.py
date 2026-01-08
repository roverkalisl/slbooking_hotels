from .models import SiteStats

class ViewCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin, static, media pages count කරන්න එපා
        if not request.path.startswith('/admin/') and not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            stats, created = SiteStats.objects.get_or_create(pk=1, defaults={'total_views': 0})
            stats.total_views += 1
            stats.save()
        
        response = self.get_response(request)
        return response