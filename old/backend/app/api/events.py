from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
from ..models.event import EventCreate, EventUpdate, EventResponse, EventRegistrationCreate, EventRegistrationUpdate, EventStats
from ..rag.policy_manager import PolicyManager

logger = logging.getLogger(__name__)

events_bp = Blueprint('events', __name__)

@events_bp.route('/create', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        try:
            event_data = EventCreate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can create events'}), 403
        
        # Validate against policies
        policy_manager = PolicyManager()
        validation = policy_manager.validate_event_registration({
            'start_datetime': event_data.start_datetime.isoformat(),
            'event_type': event_data.event_type.value
        })
        
        if not validation.get('valid', False):
            return jsonify({
                'error': 'Event validation failed',
                'details': validation
            }), 400
        
        # Generate event ID
        event_id = f"EVT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create event
        event = {
            'event_id': event_id,
            'title': event_data.title,
            'description': event_data.description,
            'event_type': event_data.event_type.value,
            'start_datetime': event_data.start_datetime,
            'end_datetime': event_data.end_datetime,
            'location': event_data.location,
            'max_participants': event_data.max_participants,
            'current_registrations': 0,
            'registration_deadline': event_data.registration_deadline,
            'created_by': current_user['user_id'],
            'requirements': event_data.requirements or [],
            'status': 'upcoming',
            'created_at': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = current_app.mongo.events.insert_one(event)
        
        # Get the created record
        created_record = current_app.mongo.events.find_one({'_id': result.inserted_id})
        created_record['id'] = str(created_record['_id'])
        del created_record['_id']
        
        logger.info(f"✅ Event created {event_id} by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event': created_record,
            'validation': validation,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/list', methods=['GET'])
@jwt_required()
def list_events():
    """List all events with filtering"""
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        event_type = request.args.get('event_type')
        status = request.args.get('status')
        created_by = request.args.get('created_by')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Build query
        query = {}
        if event_type:
            query['event_type'] = event_type
        if status:
            query['status'] = status
        if created_by:
            query['created_by'] = created_by
        
        # Get events
        events = list(current_app.mongo.events.find(
            query,
            {'_id': 0}
        ).sort('start_datetime', 1).skip(skip).limit(limit))
        
        # Get total count
        total_count = current_app.mongo.events.count_documents(query)
        
        return jsonify({
            'success': True,
            'events': events,
            'total_count': total_count,
            'limit': limit,
            'skip': skip,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event listing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/<event_id>', methods=['GET'])
@jwt_required()
def get_event(event_id):
    """Get a specific event by ID"""
    try:
        current_user = get_jwt_identity()
        
        # Get event
        event = current_app.mongo.events.find_one({'event_id': event_id}, {'_id': 0})
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Get registration count
        registration_count = current_app.mongo.event_registrations.count_documents({
            'event_id': event_id,
            'status': 'registered'
        })
        
        # Update current registrations
        current_app.mongo.events.update_one(
            {'event_id': event_id},
            {'$set': {'current_registrations': registration_count}}
        )
        event['current_registrations'] = registration_count
        
        # Check if user is registered
        user_registration = None
        if current_user['role'] == 'student':
            user_registration = current_app.mongo.event_registrations.find_one({
                'event_id': event_id,
                'student_id': current_user['user_id']
            }, {'_id': 0})
        
        return jsonify({
            'success': True,
            'event': event,
            'user_registration': user_registration,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event retrieval error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/register/<event_id>', methods=['POST'])
@jwt_required()
def register_for_event(event_id):
    """Register for an event"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is student
        if current_user['role'] != 'student':
            return jsonify({'error': 'Only students can register for events'}), 403
        
        # Get event
        event = current_app.mongo.events.find_one({'event_id': event_id})
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if event is open for registration
        if event['status'] != 'upcoming':
            return jsonify({'error': 'Event is not open for registration'}), 400
        
        # Check if registration deadline has passed
        if datetime.utcnow() > event['registration_deadline']:
            return jsonify({'error': 'Registration deadline has passed'}), 400
        
        # Check if event is full
        if event['current_registrations'] >= event['max_participants']:
            return jsonify({'error': 'Event is full'}), 400
        
        # Check if student is already registered
        existing_registration = current_app.mongo.event_registrations.find_one({
            'event_id': event_id,
            'student_id': current_user['user_id']
        })
        
        if existing_registration:
            return jsonify({'error': 'Already registered for this event'}), 400
        
        # Validate input
        try:
            registration_data = EventRegistrationCreate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Generate registration ID
        registration_id = f"REG{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create registration
        registration = {
            'registration_id': registration_id,
            'event_id': event_id,
            'student_id': current_user['user_id'],
            'registration_data': registration_data.registration_data or {},
            'status': 'registered',
            'registered_at': datetime.utcnow()
        }
        
        # Insert registration
        result = current_app.mongo.event_registrations.insert_one(registration)
        
        # Update event registration count
        current_app.mongo.events.update_one(
            {'event_id': event_id},
            {'$inc': {'current_registrations': 1}}
        )
        
        # Get the created registration
        created_registration = current_app.mongo.event_registrations.find_one({'_id': result.inserted_id})
        created_registration['id'] = str(created_registration['_id'])
        del created_registration['_id']
        
        logger.info(f"✅ Student {current_user['user_id']} registered for event {event_id}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully registered for event',
            'registration': created_registration,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/cancel-registration/<event_id>', methods=['POST'])
@jwt_required()
def cancel_registration(event_id):
    """Cancel event registration"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is student
        if current_user['role'] != 'student':
            return jsonify({'error': 'Only students can cancel registrations'}), 403
        
        # Get registration
        registration = current_app.mongo.event_registrations.find_one({
            'event_id': event_id,
            'student_id': current_user['user_id']
        })
        
        if not registration:
            return jsonify({'error': 'Registration not found'}), 404
        
        # Check if registration can be cancelled
        if registration['status'] != 'registered':
            return jsonify({'error': 'Registration cannot be cancelled'}), 400
        
        # Update registration status
        result = current_app.mongo.event_registrations.update_one(
            {'_id': registration['_id']},
            {
                '$set': {
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to cancel registration'}), 500
        
        # Update event registration count
        current_app.mongo.events.update_one(
            {'event_id': event_id},
            {'$inc': {'current_registrations': -1}}
        )
        
        logger.info(f"✅ Student {current_user['user_id']} cancelled registration for event {event_id}")
        
        return jsonify({
            'success': True,
            'message': 'Registration cancelled successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Registration cancellation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/update/<event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update an event"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can update events'}), 403
        
        # Get event
        event = current_app.mongo.events.find_one({'event_id': event_id})
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if user created the event or is coordinator
        if (current_user['role'] == 'faculty' and 
            event['created_by'] != current_user['user_id']):
            return jsonify({'error': 'Unauthorized to update this event'}), 403
        
        # Validate input
        try:
            update_data = EventUpdate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Build update document
        update_doc = {}
        if update_data.title:
            update_doc['title'] = update_data.title
        if update_data.description:
            update_doc['description'] = update_data.description
        if update_data.event_type:
            update_doc['event_type'] = update_data.event_type.value
        if update_data.start_datetime:
            update_doc['start_datetime'] = update_data.start_datetime
        if update_data.end_datetime:
            update_doc['end_datetime'] = update_data.end_datetime
        if update_data.location:
            update_doc['location'] = update_data.location
        if update_data.max_participants:
            update_doc['max_participants'] = update_data.max_participants
        if update_data.registration_deadline:
            update_doc['registration_deadline'] = update_data.registration_deadline
        if update_data.requirements:
            update_doc['requirements'] = update_data.requirements
        if update_data.status:
            update_doc['status'] = update_data.status.value
        
        if not update_doc:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_doc['updated_at'] = datetime.utcnow()
        
        # Update in MongoDB
        result = current_app.mongo.events.update_one(
            {'event_id': event_id},
            {'$set': update_doc}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update event'}), 500
        
        logger.info(f"✅ Event {event_id} updated by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Event updated successfully',
            'event_id': event_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event update error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/registrations/<event_id>', methods=['GET'])
@jwt_required()
def get_event_registrations(event_id):
    """Get registrations for an event"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get event
        event = current_app.mongo.events.find_one({'event_id': event_id})
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if user created the event or is coordinator
        if (current_user['role'] == 'faculty' and 
            event['created_by'] != current_user['user_id']):
            return jsonify({'error': 'Unauthorized to view registrations'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = {'event_id': event_id}
        if status:
            query['status'] = status
        
        # Get registrations
        registrations = list(current_app.mongo.event_registrations.find(
            query,
            {'_id': 0}
        ).sort('registered_at', -1).limit(limit))
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'registrations': registrations,
            'count': len(registrations),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event registrations error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_event_statistics():
    """Get event statistics"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build match query
        match_query = {}
        if start_date and end_date:
            match_query['created_at'] = {
                '$gte': datetime.fromisoformat(start_date),
                '$lte': datetime.fromisoformat(end_date)
            }
        
        # Calculate event statistics
        event_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        event_stats = list(current_app.mongo.events.aggregate(event_pipeline))
        
        # Calculate by event type
        type_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$event_type',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        type_stats = list(current_app.mongo.events.aggregate(type_pipeline))
        
        # Calculate registration statistics
        reg_pipeline = [
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        reg_stats = list(current_app.mongo.event_registrations.aggregate(reg_pipeline))
        
        # Calculate average registration rate
        avg_reg_pipeline = [
            {'$group': {
                '_id': '$event_id',
                'registration_count': {'$sum': 1}
            }},
            {'$group': {
                '_id': None,
                'avg_registrations': {'$avg': '$registration_count'},
                'total_events': {'$sum': 1}
            }}
        ]
        
        avg_reg_stats = list(current_app.mongo.event_registrations.aggregate(avg_reg_pipeline))
        
        return jsonify({
            'success': True,
            'statistics': {
                'events_by_status': event_stats,
                'events_by_type': type_stats,
                'registrations_by_status': reg_stats,
                'average_registrations': avg_reg_stats[0] if avg_reg_stats else {}
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event statistics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@events_bp.route('/my-events', methods=['GET'])
@jwt_required()
def get_my_events():
    """Get events created by the current user or registered by student"""
    try:
        current_user = get_jwt_identity()
        
        if current_user['role'] == 'student':
            # Get events where student is registered
            registrations = list(current_app.mongo.event_registrations.find(
                {'student_id': current_user['user_id']},
                {'event_id': 1, 'status': 1, 'registered_at': 1, '_id': 0}
            ))
            
            event_ids = [reg['event_id'] for reg in registrations]
            
            if not event_ids:
                return jsonify({
                    'success': True,
                    'events': [],
                    'registrations': []
                })
            
            # Get events
            events = list(current_app.mongo.events.find(
                {'event_id': {'$in': event_ids}},
                {'_id': 0}
            ).sort('start_datetime', 1))
            
            return jsonify({
                'success': True,
                'events': events,
                'registrations': registrations,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        else:
            # Get events created by faculty/coordinator
            events = list(current_app.mongo.events.find(
                {'created_by': current_user['user_id']},
                {'_id': 0}
            ).sort('start_datetime', 1))
            
            return jsonify({
                'success': True,
                'events': events,
                'timestamp': datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        logger.error(f"❌ My events error: {str(e)}")
        return jsonify({'error': str(e)}), 500
