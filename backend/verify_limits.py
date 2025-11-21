import sys
import os
import asyncio
from unittest.mock import MagicMock
from datetime import datetime
from fastapi import HTTPException

# Add backend to path
sys.path.append(os.getcwd())

try:
    from app.api.dependencies import check_scan_limits
    from app.models.user import User, UserPlan
    from app.models.scan import Scan
    
    print("✅ Imports successful")

    async def test_limits():
        # Mock DB session
        mock_db = MagicMock()
        
        # Case 1: Pro User (Unlimited)
        pro_user = User(id=1, email="pro@example.com", plan=UserPlan.PRO)
        result = await check_scan_limits(current_user=pro_user, db=mock_db)
        assert result == pro_user
        print("✅ Pro user allowed (unlimited)")
        
        # Case 2: Free User (Under Limit)
        free_user = User(id=2, email="free@example.com", plan=UserPlan.FREE)
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        result = await check_scan_limits(current_user=free_user, db=mock_db)
        assert result == free_user
        print("✅ Free user allowed (0 scans today)")
        
        # Case 3: Free User (Over Limit)
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        try:
            await check_scan_limits(current_user=free_user, db=mock_db)
            print("❌ Free user NOT blocked (limit reached)")
            sys.exit(1)
        except HTTPException as e:
            if e.status_code == 403:
                print("✅ Free user blocked (limit reached)")
            else:
                print(f"❌ Wrong status code: {e.status_code}")
                sys.exit(1)

    # Run async test
    asyncio.run(test_limits())

except Exception as e:
    print(f"\n❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
