"""URL routing for the parent application"""

from rest_framework.routers import DefaultRouter

from .views import *

app_name = 'allocations'

router = DefaultRouter()
router.register(r'clusters', ClusterViewSet)
router.register(r'allocations', AllocationViewSet)
router.register(r'requests', AllocationRequestViewSet)
router.register(r'reviews', AllocationRequestReviewViewSet)

urlpatterns = router.urls
