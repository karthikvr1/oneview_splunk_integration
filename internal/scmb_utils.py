#
###
# (C) Copyright (2019) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###

import os
import ssl
import amqplib.client_0_8 as amqp

from internal.utils import *

##################################################################
# Initialize certs dir.
##################################################################
def initialize_certs():
	# Create certs directory for storing the OV certificates
	certpath=os.getcwd() + os.sep + "certs"
	if not os.path.exists(certpath):
			os.makedirs(certpath)

##################################################################
# Generate RabbitMQ certs.
##################################################################
def genRabbitCa(oneview_client):
	logging.info('genRabbitCa')
	try:
		certificate_ca_signed_client = {
			"commonName": "default",
			"type": "RabbitMqClientCertV2"
		}
		oneview_client.certificate_rabbitmq.generate(certificate_ca_signed_client)
	except Exception as e:
		logging.warning("Error in generating RabbitMQCa.")
		logging.warning(e)

##################################################################
# Get RabbitMQ CA cert
##################################################################
def getCertCa(oneview_client, host):
	logging.info('getCertCa')
	cert = oneview_client.certificate_authority.get()
	ca = open('certs/' + host + '-caroot.pem', 'w+')
	ca.write(cert)
	ca.close()

##################################################################
# Get RabbitMQ KeyPair.
##################################################################			
def getRabbitKp(oneview_client, host):
	logging.info('getRabbitKp')
	try:
		cert = oneview_client.certificate_rabbitmq.get_key_pair('default')
	except Exception as e:
		if e.msg == 'Resource not found.':
			genRabbitCa(oneview_client)
			cert = oneview_client.certificate_rabbitmq.get_key_pair('default')
	ca = open('certs/' + host + '-client.pem', 'w+')
	ca.write(cert['base64SSLCertData'])
	ca.close()
	ca = open('certs/' + host + '-key.pem', 'w+')
	ca.write(cert['base64SSLKeyData'])
	ca.close()

##################################################################
# Function to stop SCMB.
# This code written based on info provided by https://www.rabbitmq.com/consumer-cancel.html
##################################################################
def stopSCMB(host):
	logging.info("stopSCMB: stopping SCMB")

	EXCHANGE_NAME = 'scmb'
	dest = host + ':5671'

	# Setup our ssl options
	ssl_options = ({'ca_certs': 'certs/' + host + '-caroot.pem',
					'certfile': 'certs/' + host + '-client.pem',
					'keyfile': 'certs/' + host + '-key.pem',
					'cert_reqs': ssl.CERT_REQUIRED,
					'ssl_version' : ssl.PROTOCOL_TLSv1_1,
					'server_side': False})

	logging.info(ssl_options)

	# Connect to RabbitMQ
	conn = amqp.Connection(dest, login_method='EXTERNAL', ssl=ssl_options)

	ch = conn.channel()
	qname, _, _ = ch.queue_declare()
	ch.queue_bind(qname, EXCHANGE_NAME, 'scmb.#')

	# Send a message to end this queue
	# basic_cancel(msg.consumer_tag)
	ch.basic_cancel(None, None)
	ch.close()
	
	
