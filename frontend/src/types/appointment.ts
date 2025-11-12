export interface TimeSlot {
  id: string;
  time: string;
  available: boolean;
}

export interface AppointmentRequest {
  propertyId: string;
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  preferredDate: string;
  preferredTime: string;
  message?: string;
  appointmentType: 'viewing' | 'consultation' | 'negotiation';
}

export interface Appointment {
  id: string;
  propertyId: string;
  propertyAddress: string;
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  scheduledDate: string;
  scheduledTime: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  appointmentType: 'viewing' | 'consultation' | 'negotiation';
  message?: string;
  createdAt: string;
  updatedAt: string;
  agentName?: string;
  agentEmail?: string;
  agentPhone?: string;
}

export interface ScheduleFormProps {
  propertyId: string;
  onSubmit: (appointment: AppointmentRequest) => void;
  onClose: () => void;
  loading?: boolean;
}

export interface AppointmentCardProps {
  appointment: Appointment;
  onCancel?: (appointmentId: string) => void;
  onReschedule?: (appointmentId: string) => void;
  className?: string;
} 