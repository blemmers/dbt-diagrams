#!/usr/bin/env python3
"""
Test the complete dbt-diagrams workflow with ERD replacement
"""
from dbt_diagrams.mermaid import (
    mermaid_erds_from_manifest_and_catalog,
    update_docs_with_rendered_mermaid_erds
)

def test_complete_workflow():
    print("=== Testing Complete Workflow ===\n")
    
    # Create realistic test manifest and catalog data
    manifest = {
        "nodes": {
            "model.test.users": {
                "name": "users",
                "alias": "users",
                "database": "analytics", 
                "schema": "public",
                "columns": {
                    "user_id": {"name": "user_id", "data_type": "INT64"},
                    "name": {"name": "name", "data_type": "STRING"},
                    "email": {"name": "email", "data_type": "STRING"}
                },
                "meta": {},
                "description": "User table\n\n```mermaid[erd='user_orders']\n```\n\nThis shows user relationships."
            },
            "model.test.orders": {
                "name": "orders", 
                "alias": "orders",
                "database": "analytics",
                "schema": "public", 
                "columns": {
                    "order_id": {"name": "order_id", "data_type": "INT64"},
                    "user_id": {"name": "user_id", "data_type": "INT64"},
                    "amount": {"name": "amount", "data_type": "DECIMAL"}
                },
                "meta": {
                    "erd": {
                        "connections": [
                            {
                                "target": "users",
                                "source_cardinality": "zero_or_more", 
                                "target_cardinality": "one",
                                "diagram": "user_orders",
                                "label": "belongs_to_user"
                            }
                        ]
                    }
                },
                "description": "Order table with ERD reference\n```mermaid[erd='user_orders']\n```"
            }
        },
        "docs": {
            "doc.test.overview": {
                "block_contents": "# Data Model Overview\n\nHere's our user-order relationship:\n\n```mermaid[erd='user_orders']\n```\n\nThis diagram shows how users relate to orders."
            }
        }
    }
    
    catalog = {
        "nodes": {
            "model.test.users": {
                "columns": {
                    "user_id": {"name": "user_id", "type": "INT64"},
                    "name": {"name": "name", "type": "STRING"}, 
                    "email": {"name": "email", "type": "STRING"}
                }
            },
            "model.test.orders": {
                "columns": {
                    "order_id": {"name": "order_id", "type": "INT64"},
                    "user_id": {"name": "user_id", "type": "INT64"},
                    "amount": {"name": "amount", "type": "DECIMAL"}
                }
            }
        }
    }
    
    print("1. Testing ERD generation from manifest/catalog:")
    try:
        rendered_erds = mermaid_erds_from_manifest_and_catalog(manifest, catalog, include_cols=True)
        
        print(f"   ✅ Generated {len(rendered_erds)} ERDs")
        
        for erd_name, erd_content in rendered_erds.items():
            print(f"\n   ERD '{erd_name}':")
            print("   " + "="*50)
            # Show first few lines
            lines = erd_content.split('\n')[:10]
            for line in lines:
                print(f"   {line}")
            if len(erd_content.split('\n')) > 10:
                print("   ...")
            print("   " + "="*50)
            
    except Exception as e:
        print(f"   ❌ ERD generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n2. Testing ERD injection into documentation:")
    try:
        # Make a copy of the manifest to test modification
        import copy
        test_manifest = copy.deepcopy(manifest)
        
        print("   Before injection:")
        print(f"     Users description: {repr(test_manifest['nodes']['model.test.users']['description'])}")
        print(f"     Overview content: {repr(test_manifest['docs']['doc.test.overview']['block_contents'])}")
        
        # This is the function that was broken
        update_docs_with_rendered_mermaid_erds(test_manifest, rendered_erds)
        
        print("\n   After injection:")
        print(f"     Users description: {repr(test_manifest['nodes']['model.test.users']['description'])}")
        print(f"     Overview content: {repr(test_manifest['docs']['doc.test.overview']['block_contents'])}")
        
        print("\n   ✅ ERD injection successful!")
        
        # Check if the injection actually worked
        users_desc = test_manifest['nodes']['model.test.users']['description']
        if 'erDiagram' in users_desc:
            print("   ✅ ERD content was properly injected into user description")
        else:
            print("   ❌ ERD content was NOT injected into user description")
            
        overview_content = test_manifest['docs']['doc.test.overview']['block_contents']
        if 'erDiagram' in overview_content:
            print("   ✅ ERD content was properly injected into overview doc")
        else:
            print("   ❌ ERD content was NOT injected into overview doc")
            
        print("\n3. Final rendered documentation samples:")
        print("\n   Users model description:")
        print("   " + "="*60)
        print("   " + users_desc.replace('\n', '\n   '))
        print("   " + "="*60)
        
        print("\n   Overview documentation:")
        print("   " + "="*60)
        print("   " + overview_content.replace('\n', '\n   '))
        print("   " + "="*60)
        
    except Exception as e:
        print(f"   ❌ ERD injection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_workflow()