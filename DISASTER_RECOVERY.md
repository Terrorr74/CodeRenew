# CodeRenew Disaster Recovery Plan

## Table of Contents
- [Overview](#overview)
- [Recovery Objectives](#recovery-objectives)
- [Backup Strategy](#backup-strategy)
- [Disaster Scenarios](#disaster-scenarios)
- [Recovery Procedures](#recovery-procedures)
- [Testing Schedule](#testing-schedule)
- [Contact Information](#contact-information)

## Overview

This document outlines the disaster recovery (DR) procedures for CodeRenew, including backup strategies, recovery time objectives (RTO), recovery point objectives (RPO), and step-by-step recovery procedures for various failure scenarios.

### Definitions

- **RTO (Recovery Time Objective)**: Maximum acceptable time that an application can be offline
- **RPO (Recovery Point Objective)**: Maximum acceptable amount of data loss measured in time
- **DR (Disaster Recovery)**: Process of restoring systems after a catastrophic failure
- **BC (Business Continuity)**: Ability to maintain business operations during a disaster

## Recovery Objectives

### Service Level Objectives

| Component | RTO | RPO | Priority |
|-----------|-----|-----|----------|
| Database (PostgreSQL) | 2 hours | 15 minutes | Critical |
| Backend API | 1 hour | 0 (stateless) | Critical |
| Frontend | 30 minutes | 0 (stateless) | High |
| File Uploads | 4 hours | 1 hour | Medium |
| Redis Cache | 15 minutes | N/A (cache) | Low |

### Impact Analysis

#### Critical (< 1 hour downtime acceptable)
- User authentication
- Payment processing
- Core scan functionality

#### High (1-4 hours downtime acceptable)
- Dashboard access
- Report viewing
- Account management

#### Medium (4-24 hours downtime acceptable)
- Email notifications
- Historical data access
- Analytics

#### Low (> 24 hours downtime acceptable)
- Marketing pages
- Blog content
- Documentation

## Backup Strategy

### Automated Backups

#### Database Backups
```bash
# Frequency: Every 6 hours
# Retention: 30 days local, 90 days off-site
# Location: /opt/coderenew/backups/ and S3

# Cron schedule (every 6 hours)
0 */6 * * * cd /opt/coderenew && ./scripts/backup-db.sh >> /var/log/coderenew-backup.log 2>&1
```

#### File Storage Backups
```bash
# Frequency: Daily at 3 AM
# Retention: 14 days
# Location: Separate storage volume

0 3 * * * rsync -av /opt/coderenew/uploads/ /backup/uploads/
```

#### Configuration Backups
```bash
# Frequency: After every change
# Retention: Indefinite (version control)
# Location: Git repository

# Environment files backup
0 0 * * 0 tar -czf /backup/config-$(date +\%Y\%m\%d).tar.gz \
  /opt/coderenew/.env.production \
  /opt/coderenew/nginx/ \
  /opt/coderenew/docker-compose*.yml
```

### Off-Site Backups

#### AWS S3 Configuration
```bash
# Install AWS CLI
apt-get install awscli

# Configure AWS credentials
aws configure

# Sync backups to S3 (daily at 4 AM)
0 4 * * * aws s3 sync /opt/coderenew/backups/ s3://coderenew-backups/database/ \
  --storage-class STANDARD_IA \
  --exclude "*" \
  --include "*.sql.gz"
```

#### Backup Verification
```bash
# Monthly backup verification script
cat > /opt/coderenew/verify-backups.sh <<'EOF'
#!/bin/bash
# Test restore to temporary database

LATEST_BACKUP=$(ls -t /opt/coderenew/backups/*.sql.gz | head -1)
echo "Testing backup: $LATEST_BACKUP"

# Create test database
docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS test_restore;"
docker-compose exec db psql -U postgres -c "CREATE DATABASE test_restore;"

# Attempt restore
gunzip -c "$LATEST_BACKUP" | docker-compose exec -T db psql -U postgres -d test_restore

if [ $? -eq 0 ]; then
    echo "✓ Backup verification successful"
    docker-compose exec db psql -U postgres -c "DROP DATABASE test_restore;"
    exit 0
else
    echo "✗ Backup verification FAILED"
    exit 1
fi
EOF

chmod +x /opt/coderenew/verify-backups.sh

# Run on 1st of every month
0 5 1 * * /opt/coderenew/verify-backups.sh
```

## Disaster Scenarios

### Scenario 1: Database Corruption

**Symptoms:**
- Database connection errors
- Data inconsistency
- PostgreSQL crash loops

**Recovery Procedure:**

1. **Assess Damage**
```bash
# Check database status
docker-compose exec db psql -U coderenew -c "SELECT version();"

# Check for corruption
docker-compose exec db psql -U coderenew -c "SELECT * FROM pg_stat_database;"
```

2. **Stop Application**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop backend frontend
```

3. **Backup Current State (if possible)**
```bash
./scripts/backup-db.sh emergency-$(date +%Y%m%d-%H%M%S)
```

4. **Restore from Latest Good Backup**
```bash
# List available backups
ls -lh backups/

# Restore
./scripts/restore-db.sh backups/coderenew_backup_YYYYMMDD_HHMMSS.sql.gz
```

5. **Verify Database Integrity**
```bash
docker-compose exec db psql -U coderenew -c "SELECT count(*) FROM users;"
docker-compose exec db psql -U coderenew -c "SELECT count(*) FROM scans;"
```

6. **Restart Application**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml start backend frontend
```

7. **Verify Application**
```bash
curl -f https://api.coderenew.com/api/v1/health
```

**Expected Recovery Time:** 1-2 hours (depends on database size)
**Data Loss:** Up to 6 hours (last backup interval)

---

### Scenario 2: Complete Server Failure

**Symptoms:**
- Server unreachable
- All services down
- Hardware failure

**Recovery Procedure:**

1. **Provision New Server**
```bash
# Minimum specs:
# - 4 CPU cores
# - 8GB RAM
# - 100GB SSD
# - Ubuntu 22.04 LTS

# Basic setup
apt-get update
apt-get install -y docker.io docker-compose git
```

2. **Restore Configuration**
```bash
# Clone repository
git clone https://github.com/yourusername/CodeRenew.git /opt/coderenew
cd /opt/coderenew

# Restore environment configuration
# (from backup or secure storage)
scp backup-server:/backup/config-latest.tar.gz .
tar -xzf config-latest.tar.gz
```

3. **Restore Database**
```bash
# Start database service only
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d db

# Download latest backup from S3
aws s3 cp s3://coderenew-backups/database/latest.sql.gz backups/

# Restore database
./scripts/restore-db.sh backups/latest.sql.gz
```

4. **Restore File Uploads**
```bash
# Sync uploads from backup storage
aws s3 sync s3://coderenew-backups/uploads/ /opt/coderenew/uploads/
```

5. **Start All Services**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

6. **Update DNS** (if IP changed)
```bash
# Update A records for:
# - coderenew.com
# - www.coderenew.com
# - api.coderenew.com
```

7. **Verify Full System**
```bash
./health-check.sh
```

**Expected Recovery Time:** 2-4 hours
**Data Loss:** Up to 6 hours for database, up to 24 hours for files

---

### Scenario 3: Ransomware Attack

**Symptoms:**
- Files encrypted
- Ransom note
- Abnormal system behavior

**Recovery Procedure:**

1. **IMMEDIATE ACTIONS**
```bash
# Disconnect from network
ifconfig eth0 down

# DO NOT pay ransom
# DO NOT try to decrypt files
```

2. **Isolate Infected Systems**
```bash
# Stop all services
docker-compose down

# Identify infection vector
# Check logs for unusual activity
grep -r "unauthorized" /var/log/
```

3. **Assess Damage**
```bash
# Check what files are encrypted
find /opt/coderenew -name "*.encrypted" -o -name "*README*"

# Verify backups are intact (off-site)
aws s3 ls s3://coderenew-backups/database/
```

4. **Provision Clean Server**
```bash
# Do NOT restore on compromised server
# Follow "Complete Server Failure" procedure on NEW server
```

5. **Restore from Known-Good Backups**
```bash
# Use backup from BEFORE infection
# Verify backup date vs. infection timeline
./scripts/restore-db.sh backups/pre-infection-backup.sql.gz
```

6. **Security Hardening**
```bash
# Update all packages
apt-get update && apt-get upgrade

# Change all passwords
# Rotate all API keys
# Review access logs

# Enable additional security measures
ufw enable
fail2ban-client start
```

7. **Forensics and Reporting**
```bash
# Preserve logs for investigation
tar -czf incident-logs-$(date +%Y%m%d).tar.gz /var/log/

# Document timeline
# Report to authorities if necessary
```

**Expected Recovery Time:** 4-8 hours
**Data Loss:** Depends on backup age before infection

---

### Scenario 4: DDoS Attack

**Symptoms:**
- Extremely high traffic
- Slow response times
- Service unavailability

**Recovery Procedure:**

1. **Identify Attack Pattern**
```bash
# Check nginx access logs
docker-compose exec nginx tail -1000 /var/log/nginx/access.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

2. **Enable Rate Limiting**
```bash
# Already configured in nginx.conf, but can be made stricter
# Edit nginx/conf.d/coderenew.conf
# Change: limit_req zone=api_limit burst=20 nodelay;
# To: limit_req zone=api_limit burst=5 nodelay;

docker-compose exec nginx nginx -s reload
```

3. **Block Attacking IPs**
```bash
# Identify attacking IPs
docker-compose exec nginx tail -10000 /var/log/nginx/access.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# Block via iptables
iptables -A INPUT -s ATTACKING_IP -j DROP

# Or via nginx
echo "deny ATTACKING_IP;" >> nginx/conf.d/blocked-ips.conf
docker-compose exec nginx nginx -s reload
```

4. **Enable CloudFlare (if available)**
```bash
# Update DNS to route through CloudFlare
# Enable "Under Attack Mode" in CloudFlare dashboard
# This provides DDoS protection and caching
```

5. **Scale Resources** (if legitimate traffic spike)
```bash
# Increase backend workers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  scale backend=3

# Increase connection limits
# Edit nginx/nginx.conf worker_connections
```

6. **Monitor and Adjust**
```bash
# Real-time monitoring
watch -n 5 'docker stats --no-stream'

# Check if attack subsided
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

**Expected Recovery Time:** 30 minutes - 2 hours
**Data Loss:** None (services continue running)

---

### Scenario 5: Data Breach

**Symptoms:**
- Unauthorized access detected
- Abnormal database queries
- User data exposed

**Recovery Procedure:**

1. **IMMEDIATE CONTAINMENT**
```bash
# Stop all external access
docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop nginx

# Enable maintenance mode
docker-compose up -d nginx-maintenance
```

2. **Assess Breach Scope**
```bash
# Check database access logs
docker-compose exec db psql -U coderenew -c \
  "SELECT usename, application_name, client_addr, state, query FROM pg_stat_activity;"

# Check for suspicious queries in logs
grep -i "DROP\|DELETE\|UPDATE\|INSERT" /var/log/postgresql/*.log

# Identify compromised accounts
docker-compose exec db psql -U coderenew -c \
  "SELECT email, last_failed_login, failed_login_attempts FROM users WHERE failed_login_attempts > 5;"
```

3. **Secure the System**
```bash
# Change all passwords immediately
# Rotate all API keys
# Revoke all sessions

docker-compose exec db psql -U coderenew -c \
  "UPDATE users SET hashed_password = 'FORCE_PASSWORD_RESET';"

# Force logout all users (clear Redis sessions)
docker-compose exec redis redis-cli FLUSHALL
```

4. **Forensics**
```bash
# Preserve evidence
tar -czf breach-evidence-$(date +%Y%m%d-%H%M%S).tar.gz \
  /var/log/ \
  /opt/coderenew/nginx/logs/ \
  /opt/coderenew/backups/

# Audit all changes in last 7 days
docker-compose exec db psql -U coderenew -c \
  "SELECT * FROM audit_log WHERE created_at > NOW() - INTERVAL '7 days';"
```

5. **Notification** (Legal Requirement)
```bash
# GDPR/Privacy Laws require breach notification
# - Within 72 hours
# - To affected users
# - To regulatory authorities

# Prepare notification
cat > breach-notification.txt <<EOF
Dear CodeRenew User,

We are writing to inform you of a data security incident...
[Include: what happened, what data, what we're doing, what you should do]
EOF
```

6. **Remediation**
```bash
# Patch vulnerabilities
# Update all dependencies
docker-compose pull

# Security audit
./security-audit.sh

# Enable additional monitoring
# Install intrusion detection system (IDS)
```

7. **Resume Operations**
```bash
# After securing system
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Send password reset emails to all users
# Force 2FA enrollment
```

**Expected Recovery Time:** 2-8 hours for containment, days/weeks for full remediation
**Data Loss:** Potentially significant user data

---

## Recovery Procedures

### Database Recovery Checklist

- [ ] Identify failure cause
- [ ] Stop application services
- [ ] Create backup of current state (if possible)
- [ ] Select appropriate backup to restore
- [ ] Verify backup integrity
- [ ] Restore database
- [ ] Run data integrity checks
- [ ] Apply any missed migrations
- [ ] Test database connectivity
- [ ] Restart application services
- [ ] Verify application functionality
- [ ] Monitor for issues
- [ ] Document incident

### Application Recovery Checklist

- [ ] Verify infrastructure health
- [ ] Pull latest stable code/images
- [ ] Restore configuration files
- [ ] Verify environment variables
- [ ] Start services in order (db → redis → backend → frontend → nginx)
- [ ] Run health checks
- [ ] Test critical user paths
- [ ] Monitor logs for errors
- [ ] Verify external integrations (Stripe, Anthropic, Resend)
- [ ] Document incident

## Testing Schedule

### Monthly Tests (1st Monday of Month)
- [ ] Backup restoration test
- [ ] Database failover test
- [ ] Health check verification

### Quarterly Tests (1st Monday of Quarter)
- [ ] Full disaster recovery drill
- [ ] Server rebuild from backups
- [ ] Update DR documentation
- [ ] Review and update contact information

### Annual Tests (January)
- [ ] Complete DR scenario testing
- [ ] Cybersecurity audit
- [ ] Review and update all procedures
- [ ] Test all backup locations
- [ ] Validate RTO/RPO targets

### Test Documentation Template

```markdown
## DR Test - [Date]
**Scenario:** [Scenario tested]
**Start Time:** [HH:MM]
**End Time:** [HH:MM]
**Total Duration:** [Minutes]

### Procedure Followed
1. [Step 1]
2. [Step 2]
...

### Issues Encountered
- [Issue 1]
- [Issue 2]

### Improvements Needed
- [Improvement 1]
- [Improvement 2]

### RTO Achieved:** [Minutes]
**RPO Achieved:** [Minutes]

**Test Result:** [PASS/FAIL]
**Conducted By:** [Name]
```

## Contact Information

### Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| System Admin | [Name] | [Phone] | [Email] |
| Database Admin | [Name] | [Phone] | [Email] |
| Security Officer | [Name] | [Phone] | [Email] |
| CTO/Technical Lead | [Name] | [Phone] | [Email] |
| CEO | [Name] | [Phone] | [Email] |

### Vendor Contacts

| Vendor | Service | Support Contact | Support URL |
|--------|---------|-----------------|-------------|
| AWS | Infrastructure | 1-XXX-XXX-XXXX | https://console.aws.amazon.com/support |
| Anthropic | AI API | support@anthropic.com | https://console.anthropic.com |
| Stripe | Payments | https://support.stripe.com | https://dashboard.stripe.com |
| Resend | Email | support@resend.com | https://resend.com/support |

### Escalation Path

1. **Initial Detection** → System Admin (immediate)
2. **Severity Assessment** → Database Admin + Security Officer (15 min)
3. **Major Incident** → CTO/Technical Lead (30 min)
4. **Critical/Extended** → CEO (1 hour)

## Documentation Updates

This document should be reviewed and updated:
- After each DR test
- After each actual incident
- Quarterly (minimum)
- When infrastructure changes
- When team members change

**Last Reviewed:** January 2025
**Next Review Due:** April 2025
**Document Owner:** [System Administrator]
**Version:** 1.0.0

---

## Appendix: Quick Reference Commands

### Emergency Stop
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop
```

### Emergency Backup
```bash
./scripts/backup-db.sh emergency-$(date +%Y%m%d-%H%M%S)
```

### Emergency Restore
```bash
./scripts/restore-db.sh backups/latest-backup.sql.gz
```

### System Status
```bash
docker-compose ps && curl -f https://api.coderenew.com/api/v1/health
```

### View Logs
```bash
docker-compose logs -f --tail=100
```
