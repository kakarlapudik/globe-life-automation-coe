# V3 Page Objects Quick Reference

## Overview
This document provides a quick reference for all V3 page objects in the RAPTOR Python Playwright framework.

## Available Page Objects

### 1. HomePage
**Module**: `raptor.pages.v3.home_page`  
**Purpose**: Main navigation and common home page operations

**Key Methods**:
- `navigate_to_home()` - Navigate to home page
- `navigate_to_user_maintenance()` - Go to User Maintenance
- `navigate_to_system_setup()` - Go to System Setup
- `navigate_to_group_contact()` - Go to Group Contact
- `navigate_to_cert_profile()` - Go to Certificate Profile
- `navigate_to_sales_rep_profile()` - Go to Sales Rep Profile
- `logout()` - Logout from application
- `is_logged_in()` - Check login status

### 2. UserMaintenance
**Module**: `raptor.pages.v3.user_maintenance`  
**Purpose**: User account management

**Key Methods**:
- `create_user(user_data)` - Create new user
- `edit_user(username, updated_data)` - Edit user
- `delete_user(username, confirm)` - Delete user
- `search_user(search_term)` - Search for users
- `get_user_details(username)` - Get user information
- `refresh_user_grid()` - Refresh user list

### 3. SystemSetup
**Module**: `raptor.pages.v3.system_setup`  
**Purpose**: System configuration and settings

**Key Methods**:
- (Implementation in progress)

### 4. GroupContact
**Module**: `raptor.pages.v3.group_contact`  
**Purpose**: Contact group management

**Key Methods**:
- `create_group(group_data)` - Create new group
- `edit_group(group_name, updated_data)` - Edit group
- `delete_group(group_name, confirm)` - Delete group
- `add_contact_to_group(group_name, contact_email, contact_data)` - Add contact
- `remove_contact_from_group(group_name, contact_email, confirm)` - Remove contact
- `search_group(search_term)` - Search for groups
- `get_group_details(group_name)` - Get group information
- `get_group_contacts(group_name)` - List group contacts

### 5. CertProfile
**Module**: `raptor.pages.v3.cert_profile`  
**Purpose**: Certificate management

**Key Methods**:
- `create_certificate_profile(cert_data)` - Create certificate profile
- `edit_certificate_profile(cert_name, updated_data)` - Edit certificate
- `delete_certificate_profile(cert_name, confirm)` - Delete certificate
- `upload_certificate(cert_name, cert_file_path, key_file_path, passphrase)` - Upload cert
- `validate_certificate(cert_name)` - Validate certificate
- `download_certificate(cert_name, download_path)` - Download certificate
- `search_certificate(search_term)` - Search for certificates
- `get_certificate_details(cert_name)` - Get certificate information

### 6. SalesRepProfile
**Module**: `raptor.pages.v3.sales_rep_profile`  
**Purpose**: Sales representative management

**Key Methods**:
- `create_sales_rep(rep_data)` - Create sales rep profile
- `edit_sales_rep(rep_name, updated_data)` - Edit sales rep
- `delete_sales_rep(rep_name, confirm)` - Delete sales rep
- `assign_customer_to_rep(rep_name, customer_name)` - Assign customer
- `search_sales_rep(search_term)` - Search for sales reps
- `get_sales_rep_details(rep_name)` - Get sales rep information
- `get_performance_metrics(rep_name)` - Get performance data
- `filter_by_territory(territory)` - Filter by territory

## Usage Examples

### Basic Navigation Flow
```python
from raptor.pages.v3 import HomePage, GroupContact

# Initialize home page
home = HomePage(page, element_manager)
await home.navigate_to_home()

# Navigate to Group Contact
await home.navigate_to_group_contact()

# Or use direct navigation
group_contact = GroupContact(page, element_manager)
await group_contact.navigate_to_group_contact()
```

### Group Management Example
```python
from raptor.pages.v3 import GroupContact

group_contact = GroupContact(page, element_manager)
await group_contact.navigate_to_group_contact()

# Create a group
await group_contact.create_group({
    "name": "Engineering Team",
    "description": "Engineering department",
    "type": "Department",
    "status": "Active"
})

# Add contacts
await group_contact.add_contact_to_group(
    "Engineering Team",
    "engineer@example.com",
    {"name": "John Engineer", "role": "Developer"}
)

# Get group details
details = await group_contact.get_group_details("Engineering Team")
print(f"Group type: {details['type']}")
```

### Certificate Management Example
```python
from raptor.pages.v3 import CertProfile

cert_profile = CertProfile(page, element_manager)
await cert_profile.navigate_to_cert_profile()

# Create certificate profile
await cert_profile.create_certificate_profile({
    "name": "Production SSL",
    "type": "TLS",
    "validity_days": "730",
    "key_size": "4096"
})

# Upload certificate
await cert_profile.upload_certificate(
    "Production SSL",
    "/path/to/cert.pem",
    "/path/to/key.pem"
)

# Validate
result = await cert_profile.validate_certificate("Production SSL")
if result["is_valid"]:
    print("Certificate is valid!")
```

### Sales Rep Management Example
```python
from raptor.pages.v3 import SalesRepProfile

sales_rep = SalesRepProfile(page, element_manager)
await sales_rep.navigate_to_sales_rep_profile()

# Create sales rep
await sales_rep.create_sales_rep({
    "name": "Jane Smith",
    "email": "jsmith@example.com",
    "territory": "West Coast",
    "commission_rate": "6.5",
    "quota": "500000"
})

# Assign customer
await sales_rep.assign_customer_to_rep(
    "Jane Smith",
    "Acme Corporation"
)

# Get performance
metrics = await sales_rep.get_performance_metrics("Jane Smith")
print(f"Quota Achievement: {metrics['quota_achievement']}%")
```

## Common Patterns

### Search and Select Pattern
```python
# Search for an item
await page_object.search_<entity>(search_term)

# Get details
details = await page_object.get_<entity>_details(name)

# Select and edit
await page_object.edit_<entity>(name, updated_data)
```

### Create-Edit-Delete Pattern
```python
# Create
await page_object.create_<entity>(data)

# Edit
await page_object.edit_<entity>(name, updated_data)

# Delete with confirmation
await page_object.delete_<entity>(name, confirm=True)
```

### Form Data Structure
All create/edit methods accept dictionaries with relevant fields:
```python
user_data = {
    "username": "jdoe",
    "email": "jdoe@example.com",
    "role": "Admin",
    "status": "Active"
}

group_data = {
    "name": "Team Name",
    "description": "Description",
    "type": "Department",
    "status": "Active"
}

cert_data = {
    "name": "Cert Name",
    "type": "TLS",
    "validity_days": "365",
    "key_size": "2048"
}

rep_data = {
    "name": "Rep Name",
    "email": "rep@example.com",
    "territory": "Region",
    "commission_rate": "5.0",
    "quota": "100000"
}
```

## Error Handling

All methods raise `RaptorException` on failure with context:
```python
try:
    await group_contact.create_group(group_data)
except RaptorException as e:
    print(f"Error: {e}")
    print(f"Context: {e.context}")
    print(f"Cause: {e.cause}")
```

## Configuration

All page objects use configuration from `ConfigManager`:
```yaml
v3:
  base_url: "https://v3.example.com"
  
timeouts:
  element: 20000
  page_load: 30000
```

## Best Practices

1. **Always wait for page load**: Use `wait_for_page_load()` after navigation
2. **Use search before operations**: Search for items before editing/deleting
3. **Handle confirmations**: Pass `confirm=True/False` to delete methods
4. **Check success messages**: Methods wait for success messages automatically
5. **Use type hints**: All methods have full type annotations
6. **Log operations**: All operations are logged automatically

## Testing

Example test structure:
```python
@pytest.mark.asyncio
async def test_group_contact_workflow(page, element_manager):
    """Test complete group contact workflow"""
    group_contact = GroupContact(page, element_manager)
    
    # Navigate
    await group_contact.navigate_to_group_contact()
    
    # Create
    await group_contact.create_group({
        "name": "Test Group",
        "type": "Department"
    })
    
    # Verify
    details = await group_contact.get_group_details("Test Group")
    assert details["name"] == "Test Group"
    
    # Cleanup
    await group_contact.delete_group("Test Group")
```

## See Also

- [Base Page Documentation](BASE_PAGE_QUICK_REFERENCE.md)
- [Table Manager Documentation](TABLE_MANAGER_GUIDE.md)
- [Element Manager Documentation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Task 18 Completion Summary](TASK_18_COMPLETION_SUMMARY.md)
