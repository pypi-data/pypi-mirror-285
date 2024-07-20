from .base import BaseAPIModelStub


class SupplierEvaluationStub(BaseAPIModelStub):
    resource_name = 'supplierEvaluations'
    default_data = {
        "frameworkFamily": "digital-outcomes-and-specialists",
        "frameworkFramework": "digital-outcomes-and-specialists",
        "frameworkSlug": "digital-outcomes-and-specialists-7",
        'lotName': 'Digital Capability and Delivery Partner',
        'lotSlug': 'digital-capability-and-delivery-partner',
        "supplierId": 886665,
        "supplierName": "Rex's Mex",
        "data": {},
        "status": "in_progress"
    }
    optional_keys = [
        ('supplierId', 'supplier_id'),
        ('frameworkSlug', 'framework_slug'),
        ('lotSlug', 'lot_slug'),
        ('lotName', 'lot_name'),
        ('data', 'data'),
        ('status', 'status'),
    ]
