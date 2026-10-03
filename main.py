from encryption_service import EncryptionService

if __name__ == '__main__':
    service = EncryptionService()

    service.save_password('Netflix', 'neydson_macedo@hotmail.com', '010205')
    
    result = service.get_password('Netflix')
    if result:
        print(f"Service found: {result['username']} -> {result['password']}")
    else:
        print("Service not found or no records available.")