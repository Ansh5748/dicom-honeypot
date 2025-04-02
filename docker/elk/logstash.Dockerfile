FROM docker.elastic.co/logstash/logstash:7.14.0

# Add custom configuration
COPY docker/elk/logstash/config/logstash.yml /usr/share/logstash/config/logstash.yml
COPY docker/elk/logstash/pipeline/ /usr/share/logstash/pipeline/

# Install plugins if needed
# RUN logstash-plugin install logstash-filter-geoip

# Set permissions
USER root
RUN chown -R logstash:logstash /usr/share/logstash/config /usr/share/logstash/pipeline
USER logstash
