"""Portfolio API endpoint exports."""

from app.api.v1.endpoints.portfolio.admin_categories import (
    router as admin_portfolio_categories_router,
)
from app.api.v1.endpoints.portfolio.admin_profile import (
    router as admin_portfolio_profile_router,
)
from app.api.v1.endpoints.portfolio.admin_project_links import (
    router as admin_portfolio_project_links_router,
)
from app.api.v1.endpoints.portfolio.admin_project_media import (
    router as admin_portfolio_project_media_router,
)
from app.api.v1.endpoints.portfolio.admin_projects import (
    router as admin_portfolio_projects_router,
)
from app.api.v1.endpoints.portfolio.admin_technologies import (
    router as admin_portfolio_technologies_router,
)
from app.api.v1.endpoints.portfolio.public import (
    router as public_portfolio_router,
)
from app.api.v1.endpoints.portfolio.public_profile import (
    router as public_portfolio_profile_router,
)


__all__ = [
    "admin_portfolio_categories_router",
    "admin_portfolio_profile_router",
    "admin_portfolio_project_links_router",
    "admin_portfolio_project_media_router",
    "admin_portfolio_projects_router",
    "admin_portfolio_technologies_router",
    "public_portfolio_profile_router",
    "public_portfolio_router",
]
