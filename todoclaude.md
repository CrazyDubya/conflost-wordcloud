# Tasks for Claude

## Authentication and User Management
1. **Create error.html template**:
   - Design a user-friendly error page template
   - Include navigation back to main areas of the site

2. **Add Email Verification**:
   - Implement email verification functionality
   - Create email templates for verification
   - Add verification status to user model

3. **Password Reset Functionality**:
   - Create forgot password route
   - Implement secure password reset process
   - Add templates for password reset flow

4. **User Profile Management**:
   - Create profile edit page
   - Allow users to update email, password, and preferences
   - Add avatar/profile picture support

## Additional Services to Implement
Each new service should follow the same credit model where 1 service use = 1 credit.

1. **File Converter Service**:
   - Support conversion between common file formats
   - PDF to/from Word, Excel, etc.
   - Image format conversion

2. **Text Analysis Tool**:
   - Text summarization
   - Entity recognition
   - Sentiment analysis
   - Keyword extraction

3. **Image Enhancement Service**:
   - Basic editing (crop, resize, adjust)
   - Filters and effects
   - Background removal
   - Image optimization

4. **Video Trimmer/Editor**:
   - Basic video trimming
   - Adding text overlays
   - Video compression
   - Format conversion

5. **Code Formatter/Linter**:
   - Support multiple programming languages
   - Format code according to style guides
   - Offer linting suggestions
   - Code beautification

## Credit System Enhancements
1. **Credit Expiration**:
   - Add expiration dates to purchased credits
   - Implement notifications for expiring credits
   - Create system to handle expired credits

2. **Subscription Model**:
   - Implement recurring subscription options
   - Monthly credit allocations
   - Subscription management interface

3. **Referral System**:
   - Allow users to earn credits by referring others
   - Create unique referral links
   - Track referral source for new signups

4. **Credit Packages Management Interface**:
   - Admin interface to add/modify credit packages
   - Support for promotional/limited-time packages
   - Bulk credit adjustment tools

## Admin Features
1. **Admin Dashboard**:
   - Overview of system usage
   - User management
   - Credit transaction monitoring
   - Service usage statistics

2. **User Management Tools**:
   - Search and filter users
   - Edit user details
   - Credit adjustment for individual users
   - Account suspension/deletion

3. **Service Management**:
   - Enable/disable services
   - Adjust credit costs
   - Set service limits

4. **Analytics Dashboard**:
   - Track service usage patterns
   - Monitor server resource usage
   - Credit purchase analytics
   - User retention metrics

## Performance Optimization
1. **Implement Caching**:
   - Set up Redis or Memcached
   - Cache frequently accessed data
   - Optimize database queries

2. **Background Task Processing**:
   - Set up Celery or similar task queue
   - Move heavy processing tasks to background workers
   - Implement progress indicators for long-running tasks

3. **API Rate Limiting**:
   - Implement rate limiting to prevent abuse
   - Set up tiered limits based on user status

4. **Database Optimization**:
   - Add indexes for frequently queried fields
   - Implement database migrations system
   - Optimize database schema