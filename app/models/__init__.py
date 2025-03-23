from app.models.user import User
from app.models.product import Category, Product, InventoryMovement
from app.models.sale import Sale, SaleItem, Payment, Return, ReturnItem
from app.models.customer import Customer, LoyaltyProgram, LoyaltyTransaction
from app.models.supplier import Supplier, PurchaseOrder, PurchaseOrderItem
from app.models.ai import AIRecommendation, AIAction, AIModel, AIInsight

# Exportar todos los modelos
__all__ = [
    'User',
    'Category', 'Product', 'InventoryMovement',
    'Sale', 'SaleItem', 'Payment', 'Return', 'ReturnItem',
    'Customer', 'LoyaltyProgram', 'LoyaltyTransaction',
    'Supplier', 'PurchaseOrder', 'PurchaseOrderItem',
    'AIRecommendation', 'AIAction', 'AIModel', 'AIInsight'
]
