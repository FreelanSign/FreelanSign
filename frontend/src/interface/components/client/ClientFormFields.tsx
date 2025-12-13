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
        <label htmlFor="address" className={styles.label}>
          Adresse
        </label>
        <textarea
          id="address"
          placeholder="123 Rue Example, 75001 Paris"
          {...register('address')}
          className={styles.textarea}
          rows={3}
          aria-invalid={!!errors.address}
          aria-describedby={errors.address ? 'address-error' : undefined}
        />
        {errors.address && (
          <small id="address-error" className={styles.error}>
            {errors.address.message}
          </small>
        )}
      </div>
    </>
  );
}
