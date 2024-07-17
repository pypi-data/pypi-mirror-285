from rest_framework.routers import DefaultRouter
from ..viewsets.{router_viewset_name} import {viewset_name}

router = DefaultRouter()
auto_api_routers = router


router.register('{api_endpoint}', {viewset_name}, basename="{viewset_name}")
