FROM docker.elastic.co/kibana/kibana:7.14.0

# Add custom configuration
COPY docker/elk/kibana/kibana.yml /usr/share/kibana/config/kibana.yml

# Set permissions
USER root
RUN chown -R kibana:kibana /usr/share/kibana/config
USER kibana
