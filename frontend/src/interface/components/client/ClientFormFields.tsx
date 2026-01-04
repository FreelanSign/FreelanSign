// frontend/src/interface/components/client/ClientFormFields.tsx

import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { ClientFormData } from './clientFormSchema';
import styles from './client-form-fields.module.css';

interface ClientFormFieldsProps {
  register: UseFormRegister<ClientFormData>;
  errors: FieldErrors<ClientFormData>;
}

export default function ClientFormFields({
  register,
  errors,
}: ClientFormFieldsProps) {
  return (
    <>
      <div className={styles.field}>
        <label htmlFor="name" className={styles.label}>
          Nom <span className={styles.required}>*</span>
        </label>
        <input
          id="name"
          type="text"
          placeholder="Entreprise SARL"
          {...register('name')}
          className={styles.input}
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <small id="name-error" className={styles.error}>
            {errors.name.message}
          </small>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor="email" className={styles.label}>
          Email
        </label>
        <input
          id="email"
          type="email"
          placeholder="contact@entreprise.com"
          {...register('email')}
          className={styles.input}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <small id="email-error" className={styles.error}>
            {errors.email.message}
          </small>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor="phone" className={styles.label}>
          Téléphone
        </label>
        <input
          id="phone"
          type="tel"
          placeholder="+33 6 12 34 56 78"
          {...register('phone')}
          className={styles.input}
          aria-invalid={!!errors.phone}
          aria-describedby={errors.phone ? 'phone-error' : undefined}
        />
        {errors.phone && (
          <small id="phone-error" className={styles.error}>
            {errors.phone.message}
          </small>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor="company" className={styles.label}>
          Entreprise
        </label>
        <input
          id="company"
          type="text"
          placeholder="Nom de l'entreprise"
          {...register('company')}
          className={styles.input}
          aria-invalid={!!errors.company}
          aria-describedby={errors.company ? 'company-error' : undefined}
        />
        {errors.company && (
          <small id="company-error" className={styles.error}>
            {errors.company.message}
          </small>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor="address_line1" className={styles.label}>
          Adresse
        </label>
        <input
          id="address_line1"
          type="text"
          placeholder="123 Rue Example"
          {...register('address_line1')}
          className={styles.input}
          aria-invalid={!!errors.address_line1}
          aria-describedby={
            errors.address_line1 ? 'address_line1-error' : undefined
          }
        />
        {errors.address_line1 && (
          <small id="address_line1-error" className={styles.error}>
            {errors.address_line1.message}
          </small>
        )}
      </div>

      <div className={styles.field}>
        <label htmlFor="address_line2" className={styles.label}>
          Complément d&apos;adresse
        </label>
        <input
          id="address_line2"
          type="text"
          placeholder="Bâtiment, Étage, Appartement"
          {...register('address_line2')}
          className={styles.input}
          aria-invalid={!!errors.address_line2}
          aria-describedby={
            errors.address_line2 ? 'address_line2-error' : undefined
          }
        />
        {errors.address_line2 && (
          <small id="address_line2-error" className={styles.error}>
            {errors.address_line2.message}
          </small>
        )}
      </div>

      <div className={styles.addressGrid}>
        <div className={styles.field}>
          <label htmlFor="postal_code" className={styles.label}>
            Code postal
          </label>
          <input
            id="postal_code"
            type="text"
            placeholder="75001"
            {...register('postal_code')}
            className={styles.input}
            aria-invalid={!!errors.postal_code}
            aria-describedby={
              errors.postal_code ? 'postal_code-error' : undefined
            }
          />
          {errors.postal_code && (
            <small id="postal_code-error" className={styles.error}>
              {errors.postal_code.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="city" className={styles.label}>
            Ville
          </label>
          <input
            id="city"
            type="text"
            placeholder="Paris"
            {...register('city')}
            className={styles.input}
            aria-invalid={!!errors.city}
            aria-describedby={errors.city ? 'city-error' : undefined}
          />
          {errors.city && (
            <small id="city-error" className={styles.error}>
              {errors.city.message}
            </small>
          )}
        </div>

        <div className={styles.field}>
          <label htmlFor="country" className={styles.label}>
            Pays
          </label>
          <input
            id="country"
            type="text"
            placeholder="FR"
            maxLength={2}
            {...register('country')}
            className={styles.input}
            aria-invalid={!!errors.country}
            aria-describedby={errors.country ? 'country-error' : undefined}
          />
          {errors.country && (
            <small id="country-error" className={styles.error}>
              {errors.country.message}
            </small>
          )}
        </div>
      </div>
    </>
  );
}
