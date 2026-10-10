#!/usr/bin/env python
"""
Admin Tool - Verify Shopkeepers
Run this script to verify pending shopkeepers
"""
from app import create_app, db
from app.models import Shopkeeper, User
from datetime import datetime

app = create_app()

def list_pending_shopkeepers():
    """List all pending shopkeepers"""
    with app.app_context():
        pending = Shopkeeper.query.filter_by(verified=False).all()
        
        if not pending:
            print("\n✓ No pending shopkeepers!\n")
            return
        
        print(f"\n{'='*80}")
        print(f"{'PENDING SHOPKEEPERS FOR VERIFICATION':^80}")
        print(f"{'='*80}\n")
        
        for idx, shop in enumerate(pending, 1):
            user = User.query.get(shop.user_id)
            print(f"{idx}. {shop.shop_name}")
            print(f"   Owner: {user.full_name} ({user.email})")
            print(f"   License: {shop.license_number}")
            print(f"   Contact: {shop.contact_number}")
            print(f"   Applied: {shop.created_at.strftime('%d %b %Y at %I:%M %p')}")
            print(f"   ID: {shop.id}")
            print()

def verify_shopkeeper(shop_id):
    """Verify a shopkeeper by ID"""
    with app.app_context():
        shop = Shopkeeper.query.get(shop_id)
        
        if not shop:
            print(f"\n✗ Shopkeeper with ID {shop_id} not found!\n")
            return False
        
        if shop.verified:
            print(f"\n⚠ {shop.shop_name} is already verified!\n")
            return False
        
        shop.verified = True
        shop.verified_at = datetime.utcnow()
        db.session.commit()
        
        print(f"\n✓ {shop.shop_name} has been verified successfully!")
        print(f"  Owner can now login and add medicines.\n")
        return True

def reject_shopkeeper(shop_id, reason=""):
    """Reject a shopkeeper"""
    with app.app_context():
        shop = Shopkeeper.query.get(shop_id)
        
        if not shop:
            print(f"\n✗ Shopkeeper with ID {shop_id} not found!\n")
            return False
        
        # You can set a rejection note in verification_notes
        shop.verification_notes = f"Rejected: {reason}" if reason else "Rejected by admin"
        db.session.commit()
        
        print(f"\n✓ {shop.shop_name} has been rejected.\n")
        return True

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*80)
    print("SHOPKEEPER VERIFICATION ADMIN TOOL".center(80))
    print("="*80 + "\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'list':
            list_pending_shopkeepers()
        elif sys.argv[1] == 'verify' and len(sys.argv) > 2:
            try:
                shop_id = int(sys.argv[2])
                verify_shopkeeper(shop_id)
            except ValueError:
                print("\n✗ Invalid shop ID! Use: python verify_shopkeeper.py verify <shop_id>\n")
        elif sys.argv[1] == 'reject' and len(sys.argv) > 2:
            try:
                shop_id = int(sys.argv[2])
                reason = sys.argv[3] if len(sys.argv) > 3 else ""
                reject_shopkeeper(shop_id, reason)
            except ValueError:
                print("\n✗ Invalid shop ID! Use: python verify_shopkeeper.py reject <shop_id> [reason]\n")
        else:
            print("Usage:")
            print("  python verify_shopkeeper.py list                    - List all pending shopkeepers")
            print("  python verify_shopkeeper.py verify <shop_id>        - Verify a shopkeeper")
            print("  python verify_shopkeeper.py reject <shop_id> [reason] - Reject a shopkeeper\n")
    else:
        list_pending_shopkeepers()
        print("\nUsage:")
        print("  python verify_shopkeeper.py list                    - List all pending shopkeepers")
        print("  python verify_shopkeeper.py verify <shop_id>        - Verify a shopkeeper")
        print("  python verify_shopkeeper.py reject <shop_id> [reason] - Reject a shopkeeper\n")
