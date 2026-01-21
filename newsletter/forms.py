import uuid
import smtplib
import socket
from email.utils import parseaddr
from django import forms
from django.core.validators import validate_email
from email_validator import validate_email as validate_email_address
from .models import Email


class EmailSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': True,
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Validate email format
        if email:
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError("Please enter a valid email address.")
        
        # Check for duplicate email
        if email and Email.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered in our database.")
        
        # Perform basic format validation with email-validator
        try:
            # Just validate the format without deliverability check
            validated_email = validate_email_address(email, check_deliverability=False)
        except ValueError:
            raise forms.ValidationError("This email address is not valid. Please enter a valid email address.")
        
        # For actual implementation, we'll attempt SMTP validation to check if email is live
        if not self.validate_smtp_email(email):
            raise forms.ValidationError("This email address does not appear to be reachable. Please enter a valid, active email address.")
        
        return email
    
    def validate_smtp_email(self, email):
        """
        Validate if an email address is deliverable using SMTP connection.
        Returns True if the email appears to be valid and reachable, False otherwise.
        """
        try:
            # Parse the email address
            parsed_email = parseaddr(email)[1]
            email_domain = parsed_email.split('@')[1]
            
            # Connect to the email domain's SMTP server
            server = smtplib.SMTP(timeout=10)
            server.set_debuglevel(0)  # Set to 1 to see SMTP communication
            
            # Get the mail exchange server for the domain
            import dns.resolver
            mx_records = dns.resolver.resolve(email_domain, 'MX')
            mx_record = sorted(mx_records, key=lambda x: x.preference)[0]
            mx_domain = str(mx_record.exchange)
            
            # Connect to the mail server
            server.connect(mx_domain, 25)
            server.helo(server.local_hostname)
            server.mail('test@example.com')
            
            # Check if the email address is accepted
            code, message = server.rcpt(parsed_email)
            server.quit()
            
            # If the SMTP server accepts the address (code 250), it likely exists
            return code == 250
            
        except ImportError:
            # If dns.resolver is not available, fall back to basic validation
            return True  # Skip SMTP validation if DNS module not available
        except (socket.gaierror, smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected):
            # Could not connect to the mail server
            return False
        except Exception:
            # Any other error during SMTP validation
            return False