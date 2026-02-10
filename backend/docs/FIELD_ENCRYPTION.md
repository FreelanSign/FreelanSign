# Field-Level Encryption Documentation

## Overview

Field-level encryption has been implemented for sensitive personal data to comply with RGPD requirements (SPECIFICATIONS_RGPD.md Section 3.1.1).

## Encrypted Fields

### Client Model (`apps/client/models.py`)
- `email` - EncryptedEmailField
- `phone` - EncryptedCharField
- `vat_number` - EncryptedCharField

### Account Model (`apps/user/models/account.py`)
- `legal_id` - EncryptedCharField (SIRET - 14 digits)

## Implementation Details

### Technology Stack
- **Encryption Algorithm**: Fernet (symmetric encryption)
- **Library**: `cryptography` (Python standard)
- **Custom Fields**: `apps/core/fields.py`
- **Database Storage**: TEXT columns storing base64-encoded ciphertext

### How It Works

1. **Automatic Encryption/Decryption**
   - Data is encrypted before saving to database
   - Data is decrypted when loading from database
   - Completely transparent to application code

2. **Database Storage**
   ```python
   # In Python code:
   client.email = "user@example.com"
   client.save()

   # In database (PostgreSQL):
   # email column stores: "gAAAAABk2X..."  (base64-encoded ciphertext)
   ```

3. **Empty Values**
   - Empty strings are stored as empty strings (not encrypted)
   - NULL values remain NULL
   - Preserves database semantics

## Configuration

### Environment Variable

**Required**: `FIELD_ENCRYPTION_KEY`

```bash
# Generate a new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env file
FIELD_ENCRYPTION_KEY="NZ4LD32PCswzIfvq4Uq0UC-JFpBOX1-YH441wuwjDWE="
```

### Settings (config/settings.py)

```python
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY")
```

## Usage

### Creating Records

```python
from apps.client.models import Client

# Create client with encrypted fields
client = Client.objects.create(
    owner=user,
    account=account,
    name="ACME Corp",
    email="contact@acme.com",  # Automatically encrypted
    phone="+33612345678",      # Automatically encrypted
    vat_number="FR12345678901" # Automatically encrypted
)

# Access decrypted values (transparent)
print(client.email)  # "contact@acme.com"
```

### Querying Records

**⚠️ IMPORTANT LIMITATION**: Encrypted fields cannot be queried using Django ORM filters.

```python
# ❌ This will NOT work (returns empty queryset):
clients = Client.objects.filter(email="contact@acme.com")

# ✅ Instead, fetch records and filter in Python:
all_clients = Client.objects.filter(account=account)
matching_clients = [c for c in all_clients if c.email == "contact@acme.com"]
```

**Why?** The database stores encrypted ciphertext, not plaintext. Django's ORM filters operate on database values, which are encrypted.

**Performance Impact**: For large datasets, consider:
- Adding unencrypted search indexes (if RGPD permits)
- Using other identifying fields (IDs, names) for queries
- Implementing application-level caching

### Updating Records

```python
# Update encrypted field (automatic encryption)
client.email = "newemail@acme.com"
client.save()

# Reload from database
client.refresh_from_db()
print(client.email)  # "newemail@acme.com" (automatically decrypted)
```

## Security Best Practices

### Key Management

1. **Development**
   - Store in `.env` file (never commit to Git)
   - Use `.env.example` for reference only

2. **Production**
   - **CRITICAL**: Migrate to AWS Secrets Manager or similar
   - Never hardcode in source code
   - Never commit to version control
   - Implement key rotation policy (annually recommended)

3. **Key Backup**
   - Store encrypted backup of key in secure location
   - Document recovery procedure
   - **Loss of key = permanent data loss**

### Encryption Key Rotation

**Current Implementation**: Manual rotation required

**Procedure** (when needed):
1. Generate new encryption key
2. Deploy migration script to re-encrypt all data:
   ```python
   # Re-save all records to trigger re-encryption
   for client in Client.objects.all():
       client.save()
   for account in Account.objects.all():
       account.save()
   ```
3. Update `FIELD_ENCRYPTION_KEY` in all environments
4. Verify data integrity

**Future Enhancement**: Implement versioned encryption keys for zero-downtime rotation.

## Migrations

### Applied Migrations

- `apps/client/migrations/0007_add_field_encryption.py`
- `apps/user/migrations/0014_add_field_encryption.py`

### Rollback (if needed)

```bash
# Rollback Client model
python manage.py migrate client 0006_add_soft_delete_to_client

# Rollback Account model
python manage.py migrate user 0013_add_soft_delete_to_account
```

**⚠️ WARNING**: Rolling back migrations will expose encrypted data as ciphertext. Requires manual decryption migration.

## Testing

### Run Encryption Tests

```bash
# Client model tests
pytest apps/client/tests/test_encryption.py -v

# Account model tests
pytest apps/user/tests/test_encryption.py -v

# All encryption tests
pytest apps/client/tests/test_encryption.py apps/user/tests/test_encryption.py -v
```

### Test Coverage

- ✅ Email encryption/decryption
- ✅ Phone encryption/decryption
- ✅ VAT number encryption/decryption
- ✅ Legal ID (SIRET) encryption/decryption
- ✅ Empty value handling
- ✅ NULL value handling
- ✅ Update operations
- ✅ Query limitations (documented)
- ✅ Soft delete preservation

## Performance Considerations

### Overhead

- **Encryption**: ~0.1ms per field write
- **Decryption**: ~0.1ms per field read
- **Storage**: ~33% increase (base64 encoding overhead)

### Optimization Tips

1. **Minimize Encrypted Field Queries**
   - Use indexed, unencrypted fields for filtering
   - Query by ID, account_id, or other identifiers

2. **Batch Operations**
   - Fetch records in batches when possible
   - Use `select_related()` and `prefetch_related()`

3. **Caching**
   - Cache decrypted values for frequently accessed records
   - Use Django's query cache for read-heavy workloads

## Troubleshooting

### Common Errors

#### `ImproperlyConfigured: FIELD_ENCRYPTION_KEY must be set`

**Solution**: Add `FIELD_ENCRYPTION_KEY` to `.env` file

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy output to .env
```

#### `cryptography.fernet.InvalidToken`

**Causes**:
- Encryption key changed after data was encrypted
- Database contains corrupted ciphertext
- Attempting to decrypt already-decrypted data

**Solution**:
- Restore original encryption key
- Re-encrypt data with new key (see Key Rotation)
- Check for data corruption in database

#### Query Returns Empty Results

**Cause**: Attempting to filter by encrypted field

**Solution**: Use Python filtering instead (see Querying Records above)

## Compliance

### RGPD Requirements Met

✅ **Data Minimization** (Art. 5.1.c)
- Only sensitive fields are encrypted
- Empty values not encrypted unnecessarily

✅ **Security of Processing** (Art. 32)
- Industry-standard Fernet encryption
- Key stored securely (environment variables)
- Access controls via application layer

✅ **Right to Erasure** (Art. 17)
- Soft delete mechanism preserves encrypted data for legal retention
- Hard delete removes all encrypted data

✅ **Data Portability** (Art. 20)
- Export functionality preserves decrypted values
- Standard JSON/CSV format supported

### Audit Trail

- Encrypted fields documented in SPECIFICATIONS_RGPD.md
- Implementation tracked in GitHub Issue #69
- Test coverage ensures encryption integrity
- Migration history preserved for compliance audits

## Future Enhancements

1. **Searchable Encryption** (if RGPD permits)
   - Implement hash-based search indexes
   - Use deterministic encryption for exact matches

2. **Key Versioning**
   - Support multiple encryption keys
   - Zero-downtime key rotation

3. **Performance Optimization**
   - Lazy decryption for bulk queries
   - Async encryption for batch operations

4. **Additional Fields**
   - `Signer.ip_address_at_signing` (when eIDAS implemented)
   - `StripeCustomer.stripe_customer_id` (when payments implemented)

## References

- **Specification**: SPECIFICATIONS_RGPD.md Section 3.1.1
- **GitHub Issue**: #69
- **Cryptography Library**: https://cryptography.io/en/latest/fernet/
- **CNIL Guidelines**: https://www.cnil.fr/fr/securite-chiffrer-garantir-lintegrite-ou-signer

## Support

For questions or issues with field encryption:
1. Check this documentation
2. Review tests in `apps/*/tests/test_encryption.py`
3. Consult SPECIFICATIONS_RGPD.md
4. Create GitHub issue with tag `security`

---

**Document Version**: 1.0
**Last Updated**: 2025-12-11
**Author**: @Bertrand2808
