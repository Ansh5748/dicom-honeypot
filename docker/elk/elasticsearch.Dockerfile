FROM docker.elastic.co/elasticsearch/elasticsearch:7.14.0

# Add custom configuration
COPY docker/elk/elasticsearch/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml

# Add plugins if needed
# RUN elasticsearch-plugin install analysis-icu

# Set permissions
USER root
RUN chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/config
USER elasticsearch
