"""HTTP layer: one Flask blueprint per feature, registered by pmo.main.create_app."""
from pmo.api import chat, closure, dashboard, digest, planning, system

BLUEPRINTS = (dashboard.bp, digest.bp, planning.bp, closure.bp, chat.bp, system.bp)   # system last: it owns the SPA catch-all
