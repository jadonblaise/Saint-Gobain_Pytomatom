"""
Local download views for testing orderbook Excel styling.
No SharePoint integration - pure local testing!
"""

from io import BytesIO
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.datalake.models import Plant
from apps.ordermanagement.logic import manage_orders
from apps.ordermanagement.models import to_exportable_dataframe
from apps.ordermanagement.porz_style import styling_of_excel_sheet

import pandas as pd
import io


@method_decorator(csrf_exempt, name="dispatch")
class DownloadOrderManagementQuickView(View):
    """
    Quick download for testing - no SharePoint, no auth, just download!
    
    Usage: 
    - Browser: http://127.0.0.1:8000/ordermanagement/download-quick/
    - Postman: GET/POST to above URL
    """
    
    def get(self, request):
        return self._download(request)
    
    def post(self, request):
        return self._download(request)
    
    def _download(self, request):
        today = timezone.localtime().date().strftime("%Y-%m-%d")
        
        try:
            # Get plant
            plant = Plant.objects.get(division="G035")
            plant_ids = [plant.id]
            
            print(f"[Quick Download] Generating orderbook for plant {plant.division}...")
            
            # Generate orderbook
            orderbook = manage_orders(plant_ids=plant_ids)
            
            # Filter for recent entries (last 30 days)
            one_month_ago = timezone.now() - timedelta(days=30)
            recent_orders = orderbook.filter(lastmodified_at__gte=one_month_ago)
            
            count = recent_orders.count()
            print(f"[Quick Download] Found {count} recent orders")
            
            if count == 0:
                return JsonResponse({
                    "message": "No orders found in the last 30 days",
                    "hint": "Import some orders first using /api/datalake/import/orders/"
                }, status=404)
            
            # Convert to DataFrame
            print("[Quick Download] Converting to DataFrame...")
            df = to_exportable_dataframe(recent_orders)
            print(f"[Quick Download] DataFrame shape: {df.shape}")
            
            # Create Excel in memory
            print("[Quick Download] Creating Excel workbook...")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=settings.OM_SHEET_NAME, index=False)
            
            print("[Quick Download] Applying styling...")
            # Apply your custom styling
            buffer = styling_of_excel_sheet(buffer=buffer, sheet_name=settings.OM_SHEET_NAME)
            buffer.seek(0)
            
            # Create response
            filename = f"orderbook-test-{today}.xlsx"
            print(f"[Quick Download] ✅ Sending file: {filename}")
            
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Plant.DoesNotExist:
            return JsonResponse({
                "message": "Plant G035 not found",
                "hint": "Make sure you've imported plant data"
            }, status=404)
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"[Quick Download] ❌ ERROR:\n{error_msg}")
            return JsonResponse({
                "message": f"Error: {str(e)}",
                "traceback": error_msg if settings.DEBUG else None
            }, status=500)